"""Output dispatch: render a service result envelope and exit with a code."""

from __future__ import annotations

import json
from typing import Any, Mapping, NoReturn

import typer
import yaml
from rich.console import Console

from ..errors import ExitCode, exit_code_for_error, format_error
from ..output import OutputFormat
from .tables import render_human

# rich auto-disables styling when stdout is not a TTY and honours NO_COLOR.
_stdout = Console()
_stderr = Console(stderr=True)


def console() -> Console:
    return _stdout


def _to_jsonable(value: Any) -> Any:
    return json.loads(json.dumps(value, default=str))


def emit(output: OutputFormat, result: Mapping[str, Any]) -> NoReturn:
    """Render a service envelope (``{ok, operation, result|error, ...}``) and exit.

    The JSON/YAML formats print the full envelope so both success and error are
    machine-parseable; the table format prints a human summary or a friendly
    error line on stderr.
    """
    ok = bool(result.get("ok"))
    code = ExitCode.OK if ok else exit_code_for_error(result.get("error") or {})

    if output is OutputFormat.JSON:
        _stdout.print_json(json.dumps(_to_jsonable(result)))
    elif output is OutputFormat.YAML:
        _stdout.print(yaml.safe_dump(_to_jsonable(result), sort_keys=False).rstrip())
    else:
        if ok:
            render_human(result, _stdout)
        else:
            _stderr.print(f"[red]{format_error(result.get('error') or {})}[/red]")

    raise typer.Exit(int(code))
