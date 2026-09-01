"""Initial command-line entry point."""

from __future__ import annotations

import typer

app = typer.Typer(no_args_is_help=True, help="Model-agnostic fiction writing harness.")


@app.callback()
def _root() -> None:
    """Run a Writer Harness command."""


@app.command()
def version() -> None:
    """Print the harness version."""

    from . import __version__

    typer.echo(__version__)


def main() -> None:
    app()
