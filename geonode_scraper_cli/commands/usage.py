"""`gscraper usage` — plan usage and limits."""

from __future__ import annotations

import typer

from ..invoke import call
from ._common import apply_output_override

usage_app = typer.Typer(help="Usage and limits.", no_args_is_help=True)


@usage_app.command("concurrency")
def concurrency(
    ctx: typer.Context,
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Check the caller's live work-concurrency slot usage against their plan limit."""
    apply_output_override(ctx, as_json, as_yaml)
    call(ctx, "get_concurrency_usage", {})
