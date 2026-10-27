"""Human-friendly rendering of service result payloads.

Designed to be defensive: the service returns plain dicts whose shape tracks the
OpenAPI spec and can change between versions. Renderers use safe access and a
generic fallback, and ``render_human`` ultimately falls back to pretty JSON for
any shape it cannot format.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from rich.console import Console
from rich.table import Table

# Long text fields (markdown/html/raw content) are summarised by length rather
# than dumped into the terminal.
_LONG_TEXT_THRESHOLD = 200

# Result keys that commonly hold a list of records worth rendering as a table.
_COLLECTION_KEYS = ("jobs", "items", "links", "results", "data")


def _is_scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _summarize_scalar(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, str) and len(value) > _LONG_TEXT_THRESHOLD:
        return f"<{len(value)} chars>"
    return str(value)


def _kv_table(data: Mapping[str, Any], console: Console, *, title: str | None = None) -> None:
    table = Table(show_header=False, box=None, title=title, title_justify="left", pad_edge=False)
    table.add_column("field", style="bold cyan", no_wrap=True)
    table.add_column("value", overflow="fold")
    for key, value in data.items():
        if _is_scalar(value):
            table.add_row(str(key), _summarize_scalar(value))
        elif isinstance(value, Mapping):
            table.add_row(str(key), _summarize_mapping(value))
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            table.add_row(str(key), f"<{len(value)} item(s)>")
        else:
            table.add_row(str(key), str(value))
    console.print(table)


def _summarize_mapping(data: Mapping[str, Any]) -> str:
    parts = []
    for key, value in data.items():
        if _is_scalar(value):
            parts.append(f"{key}={_summarize_scalar(value)}")
        else:
            parts.append(f"{key}=…")
    return ", ".join(parts) if parts else "{}"


def _records_table(records: Sequence[Mapping[str, Any]], console: Console, *, title: str | None = None) -> None:
    # Union of keys across records, preserving first-seen order; scalar columns only.
    columns: list[str] = []
    for record in records:
        if not isinstance(record, Mapping):
            # Heterogeneous / non-dict list: bail to the generic path.
            console.print_json(data=list(records))
            return
        for key, value in record.items():
            if key not in columns and _is_scalar(value):
                columns.append(key)

    if not columns:
        console.print_json(data=list(records))
        return

    table = Table(title=title, title_justify="left", header_style="bold cyan")
    for column in columns:
        table.add_column(column, overflow="fold")
    for record in records:
        table.add_row(*[_summarize_scalar(record.get(column)) for column in columns])
    console.print(table)


def _render_generic(data: Any, console: Console) -> None:
    if isinstance(data, Mapping):
        scalars = {k: v for k, v in data.items() if _is_scalar(v) or isinstance(v, Mapping)}
        if scalars:
            _kv_table(scalars, console)
        # Render the first meaningful collection field as its own table.
        for key, value in data.items():
            if (
                isinstance(value, Sequence)
                and not isinstance(value, (str, bytes, bytearray))
                and value
                and (key in _COLLECTION_KEYS or all(isinstance(item, Mapping) for item in value))
            ):
                console.print()
                _records_table(value, console, title=str(key))
                break
    elif isinstance(data, Sequence) and not isinstance(data, (str, bytes, bytearray)):
        _records_table(data, console)
    else:
        console.print(str(data))


def render_human(result: Mapping[str, Any], console: Console) -> None:
    """Render a successful service envelope's ``result`` for human consumption."""
    data = result.get("result")
    if data is None:
        operation = result.get("operation", "operation")
        console.print(f"[green]{operation}: ok[/green]")
        return
    try:
        _render_generic(data, console)
    except Exception:  # noqa: BLE001 - unfamiliar shape: never crash on rendering
        console.print_json(data=data)
