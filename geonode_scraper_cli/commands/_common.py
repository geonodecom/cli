"""Helpers shared across command modules."""

from __future__ import annotations

from typing import Iterable

import typer

from ..errors import ExitCode
from ..output import OutputFormat


def apply_output_override(ctx: typer.Context, as_json: bool, as_yaml: bool) -> None:
    """Override the output format set by the global --json/--yaml flags.

    Allows per-command placement: ``gscraper extract https://example.com --json``.
    """
    if as_json and as_yaml:
        raise typer.BadParameter("Use only one of --json or --yaml.")
    if as_json:
        ctx.obj.output = OutputFormat.JSON
    elif as_yaml:
        ctx.obj.output = OutputFormat.YAML


def parse_headers(raw_headers: Iterable[str] | None) -> dict[str, str] | None:
    """Parse repeated ``--header "Key: Value"`` flags into a dict."""
    if not raw_headers:
        return None
    headers: dict[str, str] = {}
    for item in raw_headers:
        if ":" not in item:
            typer.echo(f"Invalid header '{item}'. Expected 'Key: Value'.", err=True)
            raise typer.Exit(int(ExitCode.USAGE))
        key, value = item.split(":", 1)
        headers[key.strip()] = value.strip()
    return headers


def optional(**kwargs: object) -> dict[str, object]:
    """Drop keys whose value is ``None`` so schema defaults apply."""
    return {key: value for key, value in kwargs.items() if value is not None}
