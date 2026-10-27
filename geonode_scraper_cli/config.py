"""Configuration resolution: flag > env > TOML file > default."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib  # type: ignore[no-redef]

from geonode_scraper_tools_core import ScraperToolSettings

ENV_PREFIX = "GEONODE_SCRAPER_"
DEFAULT_PROFILE = "default"
# The production API. It used to be `http://localhost`, which is the OpenAPI
# generator's fallback for a spec with no `servers` block - harmless in a generated
# client that documents it, and wrong in a CLI a person installs and runs, where it
# means every command fails to connect until a host is configured. A flag, the
# environment or the config file still override it; this is only what happens when
# nobody said anything.
DEFAULT_HOST = "https://scraper.geonode.io"


class ConfigError(Exception):
    """Raised when required configuration is missing or a config file is invalid."""


def config_path() -> Path:
    """Location of the TOML config file, honouring ``XDG_CONFIG_HOME``."""
    override = os.environ.get(f"{ENV_PREFIX}CONFIG")
    if override:
        return Path(override).expanduser()
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return Path(base) / "geonode-scraper" / "config.toml"


def load_profiles() -> dict[str, Any]:
    path = config_path()
    if not path.exists():
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError) as exc:
        raise ConfigError(f"Could not read config file {path}: {exc}") from exc


def _env(name: str) -> str | None:
    return os.environ.get(f"{ENV_PREFIX}{name}")


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def resolve_profile_name(profile: str | None) -> str:
    return profile or _env("PROFILE") or DEFAULT_PROFILE


def resolve_settings(
    *,
    api_key: str | None = None,
    host: str | None = None,
    profile: str | None = None,
    verify_ssl: bool | None = None,
    timeout: float | None = None,
) -> ScraperToolSettings:
    """Merge CLI flags, environment, and the config-file profile into settings.

    Precedence (highest first): explicit flag, environment variable, config file,
    built-in default.
    """
    profile_name = resolve_profile_name(profile)
    profiles = load_profiles()
    file_cfg = profiles.get(profile_name) or {}
    if profile is not None and profile_name not in profiles:
        raise ConfigError(f"Profile '{profile_name}' not found in {config_path()}.")

    def pick(flag: Any, env_name: str, file_key: str, default: Any = None) -> Any:
        if flag is not None:
            return flag
        env_value = _env(env_name)
        if env_value is not None:
            return env_value
        if file_key in file_cfg:
            return file_cfg[file_key]
        return default

    resolved_host = pick(host, "HOST", "host", DEFAULT_HOST)
    resolved_key = pick(api_key, "API_KEY", "api_key")
    resolved_verify = pick(verify_ssl, "VERIFY_SSL", "verify_ssl", True)
    resolved_timeout = pick(timeout, "TIMEOUT", "timeout")

    if not resolved_key:
        raise ConfigError(
            "No API key configured. Pass --api-key, set "
            f"{ENV_PREFIX}API_KEY, or add 'api_key' to your config profile "
            f"({config_path()})."
        )

    return ScraperToolSettings(
        host=str(resolved_host),
        api_key=str(resolved_key),
        verify_ssl=_as_bool(resolved_verify),
        request_timeout=float(resolved_timeout) if resolved_timeout is not None else None,
    )
