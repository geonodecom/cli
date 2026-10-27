"""`gscraper crawl` — submit and manage site crawl jobs."""

from __future__ import annotations

from typing import List, Optional

import typer
from geonode_scraper_tools_core.schemas import (
    CreateCrawlInput,
    GetCrawlStatusInput,
    ListCrawlJobsInput,
    WaitForCrawlInput,
)

from ..invoke import call, validated
from ._common import apply_output_override, optional

crawl_app = typer.Typer(help="Submit and manage site crawl jobs.", no_args_is_help=True)


@crawl_app.command("create")
def create(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="Seed URL to start crawling from."),
    depth: int = typer.Option(2, "--depth", help="Maximum crawl depth."),
    limit: int = typer.Option(50, "--limit", help="Maximum number of pages."),
    formats: Optional[List[str]] = typer.Option(None, "--format", "-f", help="Output format(s). Repeatable."),
    render_js: bool = typer.Option(False, "--render-js", help="Render JavaScript with a headless browser."),
    same_domain_only: bool = typer.Option(
        True, "--same-domain-only/--all-domains", help="Restrict to the seed domain."
    ),
    include_subdomains: bool = typer.Option(False, "--include-subdomains", help="Include subdomains when crawling."),
    proxy_country: Optional[str] = typer.Option(None, "--proxy-country", help="ISO 3166-1 alpha-2 country code."),
    proxy_type: Optional[str] = typer.Option(None, "--proxy-type", help="Proxy type: datacenter, residential, mix."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Crawl a website from a seed URL up to a depth and page limit."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(
        CreateCrawlInput,
        url=url,
        depth=depth,
        limit=limit,
        render_js=render_js,
        same_domain_only=same_domain_only,
        include_subdomains=include_subdomains,
        **optional(formats=formats, proxy_country=proxy_country, proxy_type=proxy_type),
    )
    call(ctx, "create_crawl", payload)


@crawl_app.command("status")
def status(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Crawl job ID."),
    page: int = typer.Option(1, "--page", help="Page number."),
    page_size: int = typer.Option(10, "--page-size", help="Results per page (max 50)."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Show the status and per-page results of a crawl job."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(GetCrawlStatusInput, job_id=job_id, page=page, page_size=page_size)
    call(ctx, "get_crawl_status", payload)


@crawl_app.command("wait")
def wait(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Crawl job ID."),
    timeout_seconds: Optional[float] = typer.Option(None, "--timeout", help="Polling timeout override (seconds)."),
    poll_interval_seconds: Optional[float] = typer.Option(None, "--interval", help="Polling interval override (s)."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Poll a crawl job until it reaches a terminal state."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(
        WaitForCrawlInput,
        job_id=job_id,
        **optional(timeout_seconds=timeout_seconds, poll_interval_seconds=poll_interval_seconds),
    )
    call(ctx, "wait_for_crawl", payload)


@crawl_app.command("list")
def list_jobs(
    ctx: typer.Context,
    url: Optional[str] = typer.Option(None, "--url", help="Filter by seed URL."),
    status: Optional[str] = typer.Option(None, "--status", help="queued|processing|completed|failed|cancelled."),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="ISO 8601 lower bound."),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="ISO 8601 upper bound."),
    page: int = typer.Option(1, "--page", help="Page number."),
    page_size: int = typer.Option(100, "--page-size", help="Results per page (max 100)."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """List and filter crawl jobs."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(
        ListCrawlJobsInput,
        page=page,
        page_size=page_size,
        **optional(url=url, status=status, start_date=start_date, end_date=end_date),
    )
    call(ctx, "list_crawl_jobs", payload)


@crawl_app.command("cancel")
def cancel(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Crawl job ID to cancel."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Cancel a running crawl job."""
    apply_output_override(ctx, as_json, as_yaml)
    call(ctx, "cancel_crawl", {"job_id": job_id})
