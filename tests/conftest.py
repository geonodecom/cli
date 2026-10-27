from __future__ import annotations

from typing import Any

import pytest
from typer.testing import CliRunner


class FakeService:
    """Stand-in for ScraperToolService that records calls and returns canned envelopes."""

    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.responses = responses or {}

    def __getattr__(self, name: str):
        def method(**kwargs: Any) -> dict[str, Any]:
            self.calls.append((name, kwargs))
            if name in self.responses:
                return self.responses[name]
            return {"ok": True, "operation": name, "result": {}}

        return method


@pytest.fixture
def fake_service() -> FakeService:
    return FakeService()


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def invoke(monkeypatch, runner, fake_service, tmp_path):
    """Run the CLI with the service patched out and config isolated to a tmp file."""
    from geonode_scraper_cli.main import app

    monkeypatch.setattr("geonode_scraper_cli.context.ScraperToolService", lambda settings, **_: fake_service)

    def _invoke(args: list[str], *, env: dict[str, str] | None = None, with_key: bool = True):
        full_env = {"GEONODE_SCRAPER_CONFIG": str(tmp_path / "config.toml")}
        if with_key:
            full_env["GEONODE_SCRAPER_API_KEY"] = "test-key"
            full_env["GEONODE_SCRAPER_HOST"] = "http://api.mock.local"
        if env:
            full_env.update(env)
        return runner.invoke(app, args, env=full_env)

    return _invoke
