from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import urllib3

HEALTH = {"version": "0.1.0", "service": "scraper-api", "timestamp": "2026-01-01T00:00:00Z", "status": "ok"}


def test_requests_name_the_cli_first(runner, tmp_path):
    # The API labels a request by the first User-Agent token (scraper-api#674).
    from geonode_scraper_cli import __version__
    from geonode_scraper_cli.main import app

    response = MagicMock(status=200, reason="OK", data=json.dumps(HEALTH).encode())
    response.headers = {"content-type": "application/json"}
    env = {
        "GEONODE_SCRAPER_CONFIG": str(tmp_path / "config.toml"),
        "GEONODE_SCRAPER_API_KEY": "test-key",
        "GEONODE_SCRAPER_HOST": "http://api.mock.local",
    }

    with patch.object(urllib3.PoolManager, "request", return_value=response) as request:
        result = runner.invoke(app, ["--json", "health"], env=env)

    assert result.exit_code == 0, result.output
    assert request.call_args.kwargs["headers"]["User-Agent"].split()[0] == f"geonode-cli/{__version__}"
