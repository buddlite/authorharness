import pytest

from writer_harness.providers import (
    AuthMethod,
    Capability,
    ModelCandidate,
    ModelProfile,
    ModelRecord,
    ModelRoutingError,
    ProviderConnection,
    RoutingRequest,
    resolve_model,
)


def _connection(connection_id: str = "mimo") -> ProviderConnection:
    return ProviderConnection(
        id=connection_id,
        provider_type="openai_compatible",
        display_name="MiMo API",
        auth_method=AuthMethod.API_KEY,
    )


def test_routing_selects_first_compatible_candidate() -> None:
    profile = ModelProfile(
        id="high_volume_writer",
        display_name="High-volume writer",
        candidates=[
            ModelCandidate(model_id="small", priority=0),
            ModelCandidate(model_id="pro", priority=1),
        ],
    )
    models = {
        "small": ModelRecord(
            id="small",
            connection_id="mimo",
            provider_model_id="mimo-v2.5",
            display_name="MiMo V2.5",
            context_limit=100_000,
            output_limit=8_000,
        ),
        "pro": ModelRecord(
            id="pro",
            connection_id="mimo",
            provider_model_id="mimo-v2.5-pro",
            display_name="MiMo V2.5 Pro",
            context_limit=1_000_000,
            output_limit=32_000,
        ),
    }

    resolved = resolve_model(
        RoutingRequest(role_id="draft_writer", context_tokens=10_000),
        profile=profile,
        models=models,
        connections={"mimo": _connection()},
    )

    assert resolved.model_id == "small"
    assert resolved.provider_model_id == "mimo-v2.5"


def test_routing_skips_model_without_required_capability() -> None:
    profile = ModelProfile(
        id="vision_review",
        display_name="Vision review",
        required_capabilities={Capability.VISION},
        candidates=[ModelCandidate(model_id="text-only")],
    )
    models = {
        "text-only": ModelRecord(
            id="text-only",
            connection_id="mimo",
            provider_model_id="text-only",
            display_name="Text only",
            context_limit=10_000,
            output_limit=2_000,
        )
    }

    with pytest.raises(ModelRoutingError, match="missing capabilities"):
        resolve_model(
            RoutingRequest(role_id="vision_reviewer", context_tokens=1_000),
            profile=profile,
            models=models,
            connections={"mimo": _connection()},
        )
