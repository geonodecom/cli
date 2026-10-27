"""Map service error envelopes and exceptions to user-facing messages + exit codes."""

from __future__ import annotations

from enum import IntEnum
from typing import Any, Mapping


class ExitCode(IntEnum):
    OK = 0
    GENERIC = 1
    USAGE = 2
    AUTH = 4
    NOT_FOUND = 5
    VALIDATION = 6
    NETWORK = 7
    TIMEOUT = 8


def exit_code_for_error(error: Mapping[str, Any]) -> ExitCode:
    """Choose a POSIX exit code from a service error dict."""
    code = error.get("code")
    if code == "POLL_TIMEOUT":
        return ExitCode.TIMEOUT

    status = error.get("status")
    if status in (401, 403):
        return ExitCode.AUTH
    if status == 404:
        return ExitCode.NOT_FOUND
    if status == 422:
        return ExitCode.VALIDATION
    if status is None:
        # No HTTP status reached the server: local/connection problem.
        return ExitCode.NETWORK
    return ExitCode.GENERIC


def format_error(error: Mapping[str, Any]) -> str:
    """Build a single-line human message from a service error dict."""
    message = error.get("message") or error.get("reason") or "Request failed."
    status = error.get("status")
    code = error.get("code")
    prefix_parts = []
    if status is not None:
        prefix_parts.append(f"HTTP {status}")
    if code:
        prefix_parts.append(str(code))
    prefix = f"[{' '.join(prefix_parts)}] " if prefix_parts else ""
    return f"{prefix}{message}"
