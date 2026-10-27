"""`gscraper health` — API health check."""

from __future__ import annotations

import typer

from ..invoke import call
from ._common import apply_output_override


def health(
    ctx: typer.Context,
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Check the Scraper API health endpoint."""
    apply_output_override(ctx, as_json, as_yaml)
    call(ctx, "health_check", {})
