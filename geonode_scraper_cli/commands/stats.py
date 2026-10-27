"""`gscraper stats` — usage statistics."""

from __future__ import annotations

from typing import Optional

import typer
from geonode_scraper_tools_core.schemas import GetStatisticsInput

from ..invoke import call, validated
from ._common import apply_output_override, optional


def stats(
    ctx: typer.Context,
    start_date: Optional[str] = typer.Option(None, "--start-date", help="ISO 8601 lower bound."),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="ISO 8601 upper bound."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Show usage statistics for an optional date range."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(GetStatisticsInput, **optional(start_date=start_date, end_date=end_date))
    call(ctx, "get_statistics", payload)
