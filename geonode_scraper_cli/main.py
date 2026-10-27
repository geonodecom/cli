"""gscraper — command-line interface for the Geonode Scraper API."""

from __future__ import annotations

from typing import Optional

import typer

from . import __version__
from .commands.batch import batch_app
from .commands.config import config_app
from .commands.crawl import crawl_app
from .commands.extract import extract
from .commands.jobs import jobs_app
from .commands.map import map_app
from .commands.search import search_app
from .commands.stats import stats
from .commands.system import health
from .commands.usage import usage_app
from .context import CLIContext
from .output import OutputFormat

app = typer.Typer(
    name="gscraper",
    help="Command-line interface for the Geonode Scraper API.",
    no_args_is_help=True,
    add_completion=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"gscraper {__version__}")
        raise typer.Exit()


def _resolve_output(as_json: bool, as_yaml: bool) -> OutputFormat:
    if as_json and as_yaml:
        raise typer.BadParameter("Use only one of --json or --yaml.")
    if as_json:
        return OutputFormat.JSON
    if as_yaml:
        return OutputFormat.YAML
    return OutputFormat.TABLE


@app.callback()
def main_callback(
    ctx: typer.Context,
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key (prefer env/config over the CLI flag)."),
    host: Optional[str] = typer.Option(None, "--host", help="API base URL."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Config profile to use."),
    as_json: bool = typer.Option(False, "--json", help="Output the raw JSON envelope."),
    as_yaml: bool = typer.Option(False, "--yaml", help="Output the raw YAML envelope."),
    verify_ssl: Optional[bool] = typer.Option(None, "--verify-ssl/--no-verify-ssl", help="Verify TLS certificates."),
    timeout: Optional[float] = typer.Option(None, "--timeout", help="Request timeout in seconds."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full tracebacks on unexpected errors."),
    _version: bool = typer.Option(
        False, "--version", callback=_version_callback, is_eager=True, help="Show the version and exit."
    ),
) -> None:
    """Resolve global options into the shared CLI context."""
    ctx.obj = CLIContext(
        api_key=api_key,
        host=host,
        profile=profile,
        verify_ssl=verify_ssl,
        timeout=timeout,
        output=_resolve_output(as_json, as_yaml),
        verbose=verbose,
    )


app.command("extract")(extract)
app.command("stats")(stats)
app.command("health")(health)
app.add_typer(jobs_app, name="jobs")
app.add_typer(batch_app, name="batch")
app.add_typer(crawl_app, name="crawl")
app.add_typer(map_app, name="map")
app.add_typer(search_app, name="search")
app.add_typer(usage_app, name="usage")
app.add_typer(config_app, name="config")


if __name__ == "__main__":
    app()
