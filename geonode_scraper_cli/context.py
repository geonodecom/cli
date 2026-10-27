"""Per-invocation CLI state and lazy service construction."""

from __future__ import annotations

from dataclasses import dataclass

import typer
from geonode_scraper_tools_core import ScraperToolService, ScraperToolSettings

from . import __version__
from .config import ConfigError, resolve_settings
from .errors import ExitCode
from .output import OutputFormat


@dataclass
class CLIContext:
    """Holds resolved global options; builds the service on demand.

    Credentials are only required when a command actually calls the API, so
    ``--help``/``--version`` and the ``config`` commands never fail on a missing
    API key.
    """

    api_key: str | None
    host: str | None
    profile: str | None
    verify_ssl: bool | None
    timeout: float | None
    output: OutputFormat
    verbose: bool

    _settings: ScraperToolSettings | None = None
    _service: ScraperToolService | None = None

    def settings(self) -> ScraperToolSettings:
        if self._settings is None:
            try:
                self._settings = resolve_settings(
                    api_key=self.api_key,
                    host=self.host,
                    profile=self.profile,
                    verify_ssl=self.verify_ssl,
                    timeout=self.timeout,
                )
            except ConfigError as exc:
                typer.echo(str(exc), err=True)
                raise typer.Exit(int(ExitCode.USAGE)) from exc
        return self._settings

    def service(self) -> ScraperToolService:
        if self._service is None:
            # The API labels requests from this package `cli` (scraper-api#674).
            self._service = ScraperToolService(self.settings(), client=f"geonode-cli/{__version__}")
        return self._service


def get_cli_context(ctx: typer.Context) -> CLIContext:
    obj = ctx.obj
    assert isinstance(obj, CLIContext)  # set by the root callback
    return obj
