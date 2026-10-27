"""`gscraper batch` — submit and manage batch extraction jobs."""

from __future__ import annotations

from typing import List, Optional

import typer
from geonode_scraper_tools_core.schemas import (
    CreateBatchInput,
    GetBatchStatusInput,
    ListBatchJobsInput,
    WaitForBatchInput,
)

from ..invoke import call, validated
from ._common import apply_output_override, optional, parse_headers

batch_app = typer.Typer(help="Submit and manage batch extraction jobs.", no_args_is_help=True)


@batch_app.command("create")
def create(
    ctx: typer.Context,
    urls: List[str] = typer.Argument(..., help="One or more URLs to extract."),
    formats: Optional[List[str]] = typer.Option(None, "--format", "-f", help="Output format(s). Repeatable."),
    render_js: bool = typer.Option(False, "--render-js", help="Render JavaScript with a headless browser."),
    proxy_country: Optional[str] = typer.Option(None, "--proxy-country", help="ISO 3166-1 alpha-2 country code."),
    proxy_type: Optional[str] = typer.Option(None, "--proxy-type", help="Proxy type: datacenter, residential, mix."),
    header: Optional[List[str]] = typer.Option(None, "--header", "-H", help="Request header 'Key: Value'. Repeatable."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Submit multiple URLs in a single batch job."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(
        CreateBatchInput,
        urls=urls,
        render_js=render_js,
        **optional(
            formats=formats,
            proxy_country=proxy_country,
            proxy_type=proxy_type,
            headers=parse_headers(header),
        ),
    )
    call(ctx, "create_batch", payload)


@batch_app.command("status")
def status(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Batch job ID."),
    page: int = typer.Option(1, "--page", help="Page number."),
    page_size: int = typer.Option(10, "--page-size", help="Results per page (max 50)."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Show the status and per-URL results of a batch job."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(GetBatchStatusInput, job_id=job_id, page=page, page_size=page_size)
    call(ctx, "get_batch_status", payload)


@batch_app.command("wait")
def wait(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Batch job ID."),
    timeout_seconds: Optional[float] = typer.Option(None, "--timeout", help="Polling timeout override (seconds)."),
    poll_interval_seconds: Optional[float] = typer.Option(None, "--interval", help="Polling interval override (s)."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Poll a batch job until it reaches a terminal state."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(
        WaitForBatchInput,
        job_id=job_id,
        **optional(timeout_seconds=timeout_seconds, poll_interval_seconds=poll_interval_seconds),
    )
    call(ctx, "wait_for_batch", payload)


@batch_app.command("list")
def list_jobs(
    ctx: typer.Context,
    status: Optional[str] = typer.Option(None, "--status", help="queued|processing|completed|failed|cancelled."),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="ISO 8601 lower bound."),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="ISO 8601 upper bound."),
    page: int = typer.Option(1, "--page", help="Page number."),
    page_size: int = typer.Option(100, "--page-size", help="Results per page (max 100)."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """List and filter batch jobs."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(
        ListBatchJobsInput,
        page=page,
        page_size=page_size,
        **optional(status=status, start_date=start_date, end_date=end_date),
    )
    call(ctx, "list_batch_jobs", payload)


@batch_app.command("cancel")
def cancel(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Batch job ID to cancel."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Cancel a running batch job."""
    apply_output_override(ctx, as_json, as_yaml)
    call(ctx, "cancel_batch", {"job_id": job_id})
