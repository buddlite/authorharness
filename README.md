# Writer Harness

Writer Harness is a local-first, model-agnostic fiction-writing system. It
keeps manuscript prose and structured continuity state as separate canonical
domains, then compiles small task-specific context packets for specialist
roles.

The first implementation target is a reliable scene loop:

```text
scene state -> context packet -> planner/writer -> validation -> review -> commit
```

The architecture is designed for interchangeable providers and models. Roles
bind to named model profiles; profiles resolve through provider connections at
runtime. Connections may use API credentials, official OAuth flows, or local
endpoints.

## Development

Requires Python 3.12 or newer. With `uv`:

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

Without `uv`, create a virtual environment and install the project with the
`dev` extra using your preferred package manager.

## Initial modules

- `writer_harness.domain`: versioned story-state and scene contracts.
- `writer_harness.providers`: provider connections, model records, profiles,
  and capability-aware model resolution.
- `writer_harness.gateway`: provider-neutral async model request contracts.
- `writer_harness.cli`: initial command-line entry point.
- `writer_harness_detailed_plan.md`: architecture and phased implementation
  plan.

This repository is intentionally starting with contracts and deterministic
resolution logic before adding provider calls or persistent storage.
