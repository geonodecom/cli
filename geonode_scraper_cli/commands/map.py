"""`gscraper map` — discover URLs under a base URL."""

from __future__ import annotations

from typing import Optional

import typer
from geonode_scraper_tools_core.schemas import GetMapJobInput, ListMapJobsInput, MapUrlsInput

from ..invoke import call, validated
from ._common import apply_output_override, optional

map_app = typer.Typer(help="Discover URLs under a base URL.", no_args_is_help=True)
map_jobs_app = typer.Typer(help="Inspect map jobs.", no_args_is_help=True)
map_app.add_typer(map_jobs_app, name="jobs")


@map_app.command("run")
def run(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="Base URL to discover links from."),
    search: Optional[str] = typer.Option(None, "--search", help="Filter discovered links by substring."),
    include_subdomains: bool = typer.Option(False, "--include-subdomains/--no-subdomains", help="Include subdomains."),
    ignore_query_parameters: bool = typer.Option(
        True, "--ignore-query/--keep-query", help="Ignore query parameters when de-duplicating links."
    ),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Discover all URLs under a base URL (returns synchronously)."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(
        MapUrlsInput,
        url=url,
        include_subdomains=include_subdomains,
        ignore_query_parameters=ignore_query_parameters,
        **optional(search=search),
    )
    call(ctx, "map_urls", payload)


@map_jobs_app.command("list")
def list_jobs(
    ctx: typer.Context,
    url: Optional[str] = typer.Option(None, "--url", help="Filter by base URL."),
    status: Optional[str] = typer.Option(None, "--status", help="queued|processing|completed|failed|cancelled."),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="ISO 8601 lower bound."),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="ISO 8601 upper bound."),
    page: int = typer.Option(1, "--page", help="Page number."),
    page_size: int = typer.Option(100, "--page-size", help="Results per page (max 100)."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """List and filter map jobs."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(
        ListMapJobsInput,
        page=page,
        page_size=page_size,
        **optional(url=url, status=status, start_date=start_date, end_date=end_date),
    )
    call(ctx, "list_map_jobs", payload)


@map_jobs_app.command("get")
def get(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Map job ID."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Fetch a single map job by ID."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(GetMapJobInput, job_id=job_id)
    call(ctx, "get_map_job", payload)
