#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$root_dir"

if command -v uv >/dev/null 2>&1; then
    exec uv run --locked writer "$@"
fi

if [[ -x "$root_dir/.venv/bin/python" ]]; then
    exec "$root_dir/.venv/bin/python" -m writer_harness "$@"
fi

printf '%s\n' \
    'Writer Harness requires uv, or an existing .venv.' >&2
printf '%s\n' \
    'Install uv from https://docs.astral.sh/uv/getting-started/installation/ and run this file again.' >&2
exit 1
