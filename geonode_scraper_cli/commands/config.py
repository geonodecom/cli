"""`gscraper config` — inspect CLI configuration (read-only)."""

from __future__ import annotations

import typer

from ..config import ConfigError, config_path, load_profiles, resolve_profile_name
from ..context import get_cli_context
from ..errors import ExitCode
from ..renderers import console

config_app = typer.Typer(help="Inspect CLI configuration.", no_args_is_help=True)


@config_app.command("path")
def path() -> None:
    """Print the location of the TOML config file."""
    typer.echo(str(config_path()))


@config_app.command("show")
def show(ctx: typer.Context) -> None:
    """Show the active profile and config file contents (API keys masked)."""
    cli = get_cli_context(ctx)
    profile = resolve_profile_name(cli.profile)
    try:
        profiles = load_profiles()
    except ConfigError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(int(ExitCode.USAGE)) from exc

    out = console()
    out.print(f"config file: {config_path()}")
    out.print(f"active profile: {profile}")
    if not profiles:
        out.print("[yellow]No config file found.[/yellow]")
        return
    masked = {name: _mask(section) for name, section in profiles.items()}
    out.print_json(data=masked)


def _mask(section: object) -> object:
    if not isinstance(section, dict):
        return section
    redacted = dict(section)
    if "api_key" in redacted and redacted["api_key"]:
        redacted["api_key"] = "***"
    return redacted
