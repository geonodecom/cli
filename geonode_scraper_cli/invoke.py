"""Shared command plumbing: validate flags via tools-core schemas, call, emit."""

from __future__ import annotations

from typing import Any, NoReturn

import typer
from pydantic import BaseModel, ValidationError
from rich.console import Console

from .context import get_cli_context
from .errors import ExitCode
from .renderers import emit

_stderr = Console(stderr=True)


def validated(schema_cls: type[BaseModel], /, **kwargs: Any) -> dict[str, Any]:
    """Validate user-supplied flags through a tools-core input schema.

    Only pass keys the user actually provided; the schema fills defaults. Keeps
    validation rules (country code, ranges, enums) defined once in tools-core.
    """
    try:
        model = schema_cls(**kwargs)
    except ValidationError as exc:
        _stderr.print("[red]Invalid arguments:[/red]")
        for err in exc.errors():
            loc = ".".join(str(part) for part in err["loc"]) or "(value)"
            _stderr.print(f"  {loc}: {err['msg']}")
        raise typer.Exit(int(ExitCode.USAGE)) from exc
    return model.model_dump()


def call(ctx: typer.Context, method_name: str, payload: dict[str, Any]) -> NoReturn:
    """Invoke a service method and emit the result envelope.

    Unexpected (non-``ApiException``) failures — e.g. connection errors — are
    wrapped into an error envelope so output stays uniform; ``--verbose`` lets
    the original traceback through.
    """
    cli = get_cli_context(ctx)
    service = cli.service()
    try:
        result = getattr(service, method_name)(**payload)
    except typer.Exit:
        raise
    except Exception as exc:  # noqa: BLE001 - normalise to an error envelope
        if cli.verbose:
            raise
        result = {
            "ok": False,
            "operation": method_name,
            "error": {"status": None, "code": "CLIENT_ERROR", "message": str(exc)},
        }
    emit(cli.output, result)
