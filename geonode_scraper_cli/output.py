from __future__ import annotations

from enum import Enum


class OutputFormat(str, Enum):
    TABLE = "table"
    JSON = "json"
    YAML = "yaml"
