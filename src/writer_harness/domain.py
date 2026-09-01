"""Canonical story-state contracts.

These models deliberately describe state and proposals, not prose generation.
They are versioned boundaries between deterministic orchestration and model
roles.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class AuthorityLevel(StrEnum):
    LOCKED = "locked"
    APPROVED = "approved"
    DRAFT = "draft"
    INFERRED = "inferred"
    SPECULATIVE = "speculative"


class SceneTier(StrEnum):
    FOCUS = "focus"
    ACTIVE = "active"
    AMBIENT = "ambient"
    OFFSTAGE = "offstage"


class StateDeltaKind(StrEnum):
    ADD = "add"
    UPDATE = "update"
    CLOSE = "close"
    SUPERSEDE = "supersede"


class Evidence(StrictModel):
    source_id: str
    source_revision: int
    quote: str | None = None
    location: str | None = None


class StoryFact(StrictModel):
    id: UUID = Field(default_factory=uuid4)
    subject_id: str
    predicate: str
    value: str
    authority: AuthorityLevel = AuthorityLevel.DRAFT
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    evidence: list[Evidence] = Field(default_factory=list)
    supersedes: UUID | None = None


class CharacterState(StrictModel):
    id: str
    name: str
    stable_traits: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    needs: list[str] = Field(default_factory=list)
    desires: list[str] = Field(default_factory=list)
    false_beliefs: list[str] = Field(default_factory=list)
    current_goal: str | None = None
    concealed_goal: str | None = None
    knows: list[str] = Field(default_factory=list)
    suspects: list[str] = Field(default_factory=list)
    false_beliefs_in_play: list[str] = Field(default_factory=list)
    must_not_know: list[str] = Field(default_factory=list)
    location_id: str | None = None
    condition: str | None = None
    possessions: list[str] = Field(default_factory=list)
    commitments: list[str] = Field(default_factory=list)
    secrets: list[str] = Field(default_factory=list)
    recent_emotional_state: str | None = None
    voice_anchors: list[str] = Field(default_factory=list)
    last_scene_id: str | None = None


class SceneParticipant(StrictModel):
    character_id: str
    tier: SceneTier
    starting_location: str | None = None
    can_observe: list[str] = Field(default_factory=list)
    required_presence: bool = False


class InteractionEdge(StrictModel):
    source_character_id: str
    target_character_id: str
    pressure: str
    scene_business: str | None = None
    knowledge_asymmetry: str | None = None


class Beat(StrictModel):
    id: str
    order: int = Field(ge=0)
    summary: str
    initiator_id: str | None = None
    target_ids: list[str] = Field(default_factory=list)
    observer_ids: list[str] = Field(default_factory=list)
    required_reactions: list[str] = Field(default_factory=list)
    surface_effect: str | None = None
    hidden_effect: str | None = None
    state_changes: list[str] = Field(default_factory=list)
    completed: bool = False


class IntentCard(StrictModel):
    character_id: str
    public_objective: str
    private_objective: str | None = None
    starting_emotion: str | None = None
    knows: list[str] = Field(default_factory=list)
    does_not_know: list[str] = Field(default_factory=list)
    wants_from: dict[str, str] = Field(default_factory=dict)
    will_volunteer: list[str] = Field(default_factory=list)
    will_conceal: list[str] = Field(default_factory=list)
    likely_tactics: list[str] = Field(default_factory=list)
    boundary: str | None = None
    desired_end_state: str | None = None
    required_action_or_reaction: str | None = None


class SceneContract(StrictModel):
    scene_id: str
    title: str | None = None
    pov_character_id: str
    purpose: str
    entry_state: str
    exit_state: str
    participants: list[SceneParticipant] = Field(default_factory=list)
    intent_cards: list[IntentCard] = Field(default_factory=list)
    interaction_edges: list[InteractionEdge] = Field(default_factory=list)
    beats: list[Beat] = Field(default_factory=list)
    location_id: str | None = None
    timeline_position: str | None = None
    tense: str = "past"
    viewpoint: str = "limited"
    locked_requirements: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)


class StateDelta(StrictModel):
    id: UUID = Field(default_factory=uuid4)
    kind: StateDeltaKind
    entity_type: str
    entity_id: str
    field: str | None = None
    proposed_value: str | None = None
    rationale: str
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    evidence: list[Evidence] = Field(default_factory=list)
    proposed_at: datetime = Field(default_factory=datetime.utcnow)
