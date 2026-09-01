"""Provider connections, model profiles, and deterministic model selection."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class AuthMethod(StrEnum):
    API_KEY = "api_key"
    OAUTH = "oauth"
    BEARER_TOKEN = "bearer_token"
    NONE = "none"


class Capability(StrEnum):
    TEXT = "text"
    VISION = "vision"
    AUDIO = "audio"
    TOOLS = "tools"
    STRUCTURED_OUTPUT = "structured_output"
    STREAMING = "streaming"


class ProviderConnection(StrictModel):
    id: str
    provider_type: str
    display_name: str
    auth_method: AuthMethod
    credential_ref: str | None = None
    base_url: str | None = None
    enabled: bool = True
    privacy_tags: set[str] = Field(default_factory=set)
    quota_group: str | None = None


class ModelRecord(StrictModel):
    id: str
    connection_id: str
    provider_model_id: str
    display_name: str
    capabilities: set[Capability] = Field(default_factory=lambda: {Capability.TEXT})
    context_limit: int = Field(gt=0)
    output_limit: int = Field(gt=0)
    family: str | None = None
    enabled: bool = True
    cost_tier: int = Field(default=1, ge=0)


class ModelCandidate(StrictModel):
    model_id: str
    priority: int = Field(default=0, ge=0)
    max_cost_tier: int | None = Field(default=None, ge=0)


class ModelProfile(StrictModel):
    id: str
    display_name: str
    required_capabilities: set[Capability] = Field(default_factory=lambda: {Capability.TEXT})
    preferred_capabilities: set[Capability] = Field(default_factory=set)
    candidates: list[ModelCandidate] = Field(default_factory=list)
    max_context: int | None = Field(default=None, gt=0)
    max_cost_tier: int | None = Field(default=None, ge=0)
    require_independent_family: bool = False
    allowed_privacy_tags: set[str] = Field(default_factory=set)


class RoleBinding(StrictModel):
    role_id: str
    profile_id: str
    scope: str = "default"


class RoutingRequest(StrictModel):
    role_id: str
    context_tokens: int = Field(gt=0)
    required_capabilities: set[Capability] = Field(default_factory=lambda: {Capability.TEXT})
    max_cost_tier: int | None = Field(default=None, ge=0)
    privacy_tags: set[str] = Field(default_factory=set)
    excluded_families: set[str] = Field(default_factory=set)


class ResolvedModel(StrictModel):
    profile_id: str
    model_id: str
    connection_id: str
    provider_model_id: str
    reason: str


class ModelRoutingError(RuntimeError):
    """Raised when no connected model satisfies a role's requirements."""


def resolve_model(
    request: RoutingRequest,
    *,
    profile: ModelProfile,
    models: dict[str, ModelRecord],
    connections: dict[str, ProviderConnection],
) -> ResolvedModel:
    """Resolve a role request without calling a provider.

    This pure function is intentionally dependency-injected and deterministic,
    making model switching and routing decisions easy to test and audit.
    """

    required = profile.required_capabilities | request.required_capabilities
    max_cost = _minimum_limit(profile.max_cost_tier, request.max_cost_tier)
    candidates = sorted(profile.candidates, key=lambda item: item.priority)

    failures: list[str] = []
    for candidate in candidates:
        model = models.get(candidate.model_id)
        if model is None:
            failures.append(f"{candidate.model_id}: unknown model")
            continue
        connection = connections.get(model.connection_id)
        if connection is None or not connection.enabled:
            failures.append(f"{candidate.model_id}: connection unavailable")
            continue
        if not model.enabled:
            failures.append(f"{candidate.model_id}: model disabled")
            continue
        if not required <= model.capabilities:
            failures.append(f"{candidate.model_id}: missing capabilities")
            continue
        if profile.max_context is not None and model.context_limit < profile.max_context:
            failures.append(f"{candidate.model_id}: profile context requirement not met")
            continue
        if model.context_limit < request.context_tokens:
            failures.append(f"{candidate.model_id}: request context too large")
            continue
        candidate_limit = _minimum_limit(max_cost, candidate.max_cost_tier)
        if candidate_limit is not None and model.cost_tier > candidate_limit:
            failures.append(f"{candidate.model_id}: cost tier exceeds limit")
            continue
        if request.privacy_tags and not request.privacy_tags <= connection.privacy_tags:
            failures.append(f"{candidate.model_id}: privacy tags not allowed")
            continue
        if model.family is not None and model.family in request.excluded_families:
            failures.append(f"{candidate.model_id}: model family excluded")
            continue
        if profile.require_independent_family and model.family is None:
            failures.append(f"{candidate.model_id}: family unknown for independence check")
            continue
        return ResolvedModel(
            profile_id=profile.id,
            model_id=model.id,
            connection_id=connection.id,
            provider_model_id=model.provider_model_id,
            reason=f"selected priority {candidate.priority} candidate for role {request.role_id}",
        )

    detail = "; ".join(failures) if failures else "profile has no candidates"
    raise ModelRoutingError(f"No compatible model for {request.role_id}: {detail}")


def _minimum_limit(first: int | None, second: int | None) -> int | None:
    if first is None:
        return second
    if second is None:
        return first
    return min(first, second)
