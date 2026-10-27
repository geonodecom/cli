"""`gscraper jobs` — inspect and wait on extraction jobs."""

from __future__ import annotations

from typing import Optional

import typer
from geonode_scraper_tools_core.schemas import GetJobResultInput, ListJobsInput, WaitForJobInput

from ..invoke import call, validated
from ._common import apply_output_override, optional

jobs_app = typer.Typer(help="Inspect and wait on extraction jobs.", no_args_is_help=True)


@jobs_app.command("get")
def get(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Extraction job ID."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Fetch the current state or final result of an extraction job."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(GetJobResultInput, job_id=job_id)
    call(ctx, "get_job_result", payload)


@jobs_app.command("list")
def list_jobs(
    ctx: typer.Context,
    job_id: Optional[str] = typer.Option(None, "--job-id", help="Filter by job ID."),
    url: Optional[str] = typer.Option(None, "--url", help="Filter by target URL."),
    status: Optional[str] = typer.Option(None, "--status", help="queued|processing|completed|failed|cancelled."),
    output: Optional[str] = typer.Option(None, "--output-format", help="Filter by requested output: markdown|html."),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="ISO 8601 lower bound."),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="ISO 8601 upper bound."),
    page: int = typer.Option(1, "--page", help="Page number."),
    page_size: int = typer.Option(100, "--page-size", help="Results per page (max 100)."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """List and filter extraction jobs."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(
        ListJobsInput,
        page=page,
        page_size=page_size,
        **optional(
            job_id=job_id,
            url=url,
            status=status,
            output=output,
            start_date=start_date,
            end_date=end_date,
        ),
    )
    call(ctx, "list_jobs", payload)


@jobs_app.command("wait")
def wait(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Extraction job ID."),
    timeout_seconds: Optional[float] = typer.Option(None, "--timeout", help="Polling timeout override (seconds)."),
    poll_interval_seconds: Optional[float] = typer.Option(None, "--interval", help="Polling interval override (s)."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Poll an extraction job until it reaches a terminal state."""
    apply_output_override(ctx, as_json, as_yaml)
    payload = validated(
        WaitForJobInput,
        job_id=job_id,
        **optional(timeout_seconds=timeout_seconds, poll_interval_seconds=poll_interval_seconds),
    )
    call(ctx, "wait_for_job", payload)
