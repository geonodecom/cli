"""`gscraper search` — run a search query and inspect search jobs."""

from __future__ import annotations

from typing import Optional

import typer
from geonode_scraper_tools_core.schemas import GetSearchJobInput, ListSearchJobsInput, SearchInput

from ..invoke import call, validated
from ._common import apply_output_override, optional

search_app = typer.Typer(help="Run search queries and inspect search jobs.", no_args_is_help=True)
search_jobs_app = typer.Typer(help="Inspect search jobs.", no_args_is_help=True)
search_app.add_typer(search_jobs_app, name="jobs")


@search_app.command("run")
def run(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Search query."),
    locale: Optional[str] = typer.Option(None, "--locale", help="Locale tag, e.g. 'en' or 'en-US'."),
    page: int = typer.Option(1, "--page", help="Result page to fetch (1-20)."),
    safe: str = typer.Option("off", "--safe", help="Safe-search level: off|moderate|strict."),
    time_range: Optional[str] = typer.Option(None, "--time-range", help="day|week|month|year."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Run a search query (returns synchronously)."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(
        SearchInput,
        query=query,
        page=page,
        safe=safe,
        **optional(locale=locale, time_range=time_range),
    )
    call(ctx, "search", payload)


@search_jobs_app.command("list")
def list_jobs(
    ctx: typer.Context,
    query: Optional[str] = typer.Option(None, "--query", help="Filter by search query."),
    status: Optional[str] = typer.Option(None, "--status", help="queued|processing|completed|failed|cancelled."),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="ISO 8601 lower bound."),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="ISO 8601 upper bound."),
    page: int = typer.Option(1, "--page", help="Page number."),
    page_size: int = typer.Option(100, "--page-size", help="Results per page (max 100)."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """List and filter search jobs."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(
        ListSearchJobsInput,
        page=page,
        page_size=page_size,
        **optional(query=query, status=status, start_date=start_date, end_date=end_date),
    )
    call(ctx, "list_search_jobs", payload)


@search_jobs_app.command("get")
def get(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Search job ID."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Fetch a single search job by ID."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(GetSearchJobInput, job_id=job_id)
    call(ctx, "get_search_job", payload)
