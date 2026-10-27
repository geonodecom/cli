"""`gscraper extract` — extract content from a single URL."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer
from geonode_scraper_tools_core.schemas import ExtractInput

from ..context import get_cli_context
from ..errors import ExitCode
from ..invoke import call, validated
from ..renderers import emit
from ._common import apply_output_override, optional, parse_headers


def extract(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="URL to extract content from."),
    formats: Optional[List[str]] = typer.Option(
        None, "--format", "-f", help="Output format(s): markdown, html. Repeatable."
    ),
    render_js: bool = typer.Option(False, "--render-js", help="Render JavaScript with a headless browser."),
    is_async: bool = typer.Option(False, "--async", "-a", help="Submit as an async job instead of waiting inline."),
    proxy_country: Optional[str] = typer.Option(None, "--proxy-country", help="ISO 3166-1 alpha-2 country code."),
    proxy_type: Optional[str] = typer.Option(None, "--proxy-type", help="Proxy type: datacenter, residential, mix."),
    header: Optional[List[str]] = typer.Option(None, "--header", "-H", help="Request header 'Key: Value'. Repeatable."),
    wait_for: Optional[str] = typer.Option(
        None, "--wait-for", help="CSS/XPath selector to wait for (browser only, requires --render-js)."
    ),
    wait_timeout: Optional[int] = typer.Option(
        None, "--wait-timeout", help="Pause in ms after wait_for (0-30000, requires --render-js)."
    ),
    wait_until: Optional[str] = typer.Option(
        None, "--wait-until", help="Lifecycle event: load, networkidle, ... (requires --render-js)."
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write the extracted content (markdown/html) to this file."
    ),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output raw YAML envelope."),
) -> None:
    """Extract content from URL. Sync by default; use --async to queue a job."""
    apply_output_override(ctx, as_json, as_yaml)

    if (wait_for is not None or wait_timeout is not None or wait_until is not None) and not render_js:
        typer.echo("--wait-for, --wait-until, and --wait-timeout require --render-js.", err=True)
        raise typer.Exit(int(ExitCode.USAGE))

    payload = validated(
        ExtractInput,
        url=url,
        render_js=render_js,
        processing_mode="async" if is_async else "sync",
        **optional(
            formats=formats,
            proxy_country=proxy_country,
            proxy_type=proxy_type,
            headers=parse_headers(header),
            wait_for=wait_for,
            wait_timeout=wait_timeout,
            wait_until=wait_until,
        ),
    )

    if output_file is None:
        call(ctx, "extract", payload)

    # --output: call once, write the content body, then emit the same envelope.
    cli = get_cli_context(ctx)
    result = cli.service().extract(**payload)
    if result.get("ok"):
        data = (result.get("result") or {}).get("data") or {}
        content = data.get("markdown") or data.get("html") or ""
        output_file.write_text(content, encoding="utf-8")
        typer.echo(f"Wrote {len(content)} chars to {output_file}", err=True)
    emit(cli.output, result)
