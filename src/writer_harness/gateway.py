"""Provider-neutral asynchronous model gateway contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .providers import ModelRecord, ProviderConnection


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True, slots=True)
class ModelRequest:
    messages: tuple[ChatMessage, ...]
    max_output_tokens: int
    temperature: float | None = None
    response_schema: dict[str, object] | None = None


@dataclass(frozen=True, slots=True)
class ModelResponse:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    provider_request_id: str | None = None


class ModelGateway(Protocol):
    async def complete(
        self,
        request: ModelRequest,
        *,
        model: ModelRecord,
        connection: ProviderConnection,
    ) -> ModelResponse:
        """Execute one model request through a resolved connection."""


class CredentialStore(Protocol):
    async def get(self, credential_ref: str) -> str | None:
        """Return a secret by opaque reference, never by provider model ID."""

    async def set(self, credential_ref: str, secret: str) -> None:
        """Persist a secret using an OS-backed or explicitly configured store."""

    async def delete(self, credential_ref: str) -> None:
        """Delete a stored secret."""
