from __future__ import annotations

import json


def test_version(invoke):
    result = invoke(["--version"], with_key=False)
    assert result.exit_code == 0
    assert "gscraper" in result.stdout


def test_health_success_table(invoke, fake_service):
    fake_service.responses["health_check"] = {
        "ok": True,
        "operation": "health_check",
        "result": {"status": "ok", "service": "scraper-api", "version": "0.3.0"},
    }
    result = invoke(["health"])
    assert result.exit_code == 0
    assert "status" in result.stdout
    assert ("health_check", {}) in fake_service.calls


def test_health_json_envelope(invoke, fake_service):
    fake_service.responses["health_check"] = {
        "ok": True,
        "operation": "health_check",
        "result": {"status": "ok"},
    }
    result = invoke(["--json", "health"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["result"]["status"] == "ok"


def test_json_flag_after_subcommand(invoke, fake_service):
    fake_service.responses["health_check"] = {
        "ok": True,
        "operation": "health_check",
        "result": {"status": "ok"},
    }
    result = invoke(["health", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True


def test_extract_passes_validated_payload(invoke, fake_service):
    result = invoke(["extract", "https://example.com", "-f", "markdown", "--render-js"])
    assert result.exit_code == 0
    name, kwargs = fake_service.calls[-1]
    assert name == "extract"
    assert kwargs["url"] == "https://example.com"
    assert kwargs["formats"] == ["markdown"]
    assert kwargs["render_js"] is True
    assert kwargs["processing_mode"] == "sync"


def test_extract_async_flag(invoke, fake_service):
    invoke(["extract", "https://example.com", "--async"])
    _, kwargs = fake_service.calls[-1]
    assert kwargs["processing_mode"] == "async"


def test_extract_invalid_proxy_country_is_usage_error(invoke, fake_service):
    result = invoke(["extract", "https://example.com", "--proxy-country", "usa"])
    assert result.exit_code == 2
    assert not fake_service.calls  # validation fails before the service is called


def test_extract_browser_options_require_render_js(invoke, fake_service):
    result = invoke(["extract", "https://example.com", "--wait-for", ".content"])
    assert result.exit_code == 2
    assert "--render-js" in result.stderr
    assert not fake_service.calls


def test_error_envelope_maps_exit_code(invoke, fake_service):
    fake_service.responses["get_job_result"] = {
        "ok": False,
        "operation": "get_job_result",
        "error": {"status": 404, "code": "NOT_FOUND", "message": "Job not found."},
    }
    result = invoke(["jobs", "get", "missing-id"])
    assert result.exit_code == 5
    assert "Job not found." in result.stderr


def test_missing_api_key_is_usage_error(invoke, fake_service):
    result = invoke(["health"], with_key=False)
    assert result.exit_code == 2
    assert "No API key configured" in result.stderr
    assert not fake_service.calls


def test_flag_overrides_env_host(invoke, fake_service, monkeypatch):
    captured: dict[str, object] = {}

    def _capture(settings, **_):
        captured["host"] = settings.host
        return fake_service

    monkeypatch.setattr("geonode_scraper_cli.context.ScraperToolService", _capture)
    result = invoke(["--host", "https://flag.example", "health"])
    assert result.exit_code == 0
    assert captured["host"] == "https://flag.example"


def test_batch_cancel_calls_service(invoke, fake_service):
    invoke(["batch", "cancel", "00000000-0000-0000-0000-000000000002"])
    name, kwargs = fake_service.calls[-1]
    assert name == "cancel_batch"
    assert kwargs == {"job_id": "00000000-0000-0000-0000-000000000002"}


def test_crawl_cancel_calls_service(invoke, fake_service):
    invoke(["crawl", "cancel", "00000000-0000-0000-0000-000000000003"])
    name, _ = fake_service.calls[-1]
    assert name == "cancel_crawl"


def test_map_run_renders_links(invoke, fake_service):
    fake_service.responses["map_urls"] = {
        "ok": True,
        "operation": "map_urls",
        "result": {"links": [{"url": "https://a.com", "source": "sitemap"}]},
    }
    result = invoke(["map", "run", "https://example.com"])
    assert result.exit_code == 0
    assert "https://a.com" in result.stdout


def test_map_run_defaults_include_subdomains_false(invoke, fake_service):
    invoke(["map", "run", "https://example.com"])
    _, kwargs = fake_service.calls[-1]
    assert kwargs["include_subdomains"] is False


def test_search_run_passes_validated_payload(invoke, fake_service):
    fake_service.responses["search"] = {
        "ok": True,
        "operation": "search",
        "result": {"job_id": "00000000-0000-0000-0000-000000000007", "results": []},
    }
    result = invoke(["search", "run", "geonode scraper api", "--page", "2", "--safe", "moderate"])
    assert result.exit_code == 0
    name, kwargs = fake_service.calls[-1]
    assert name == "search"
    assert kwargs["query"] == "geonode scraper api"
    assert kwargs["page"] == 2
    assert kwargs["safe"] == "moderate"


def test_search_jobs_list_calls_service(invoke, fake_service):
    invoke(["search", "jobs", "list", "--query", "geonode", "--status", "completed"])
    name, kwargs = fake_service.calls[-1]
    assert name == "list_search_jobs"
    assert kwargs["query"] == "geonode"
    assert kwargs["status"] == "completed"


def test_search_jobs_get_calls_service(invoke, fake_service):
    invoke(["search", "jobs", "get", "00000000-0000-0000-0000-000000000008"])
    name, kwargs = fake_service.calls[-1]
    assert name == "get_search_job"
    assert kwargs == {"job_id": "00000000-0000-0000-0000-000000000008"}


def test_usage_concurrency_calls_service(invoke, fake_service):
    fake_service.responses["get_concurrency_usage"] = {
        "ok": True,
        "operation": "get_concurrency_usage",
        "result": {"work_concurrency_in_use": 2, "work_concurrency_limit": 10},
    }
    result = invoke(["usage", "concurrency"])
    assert result.exit_code == 0
    name, kwargs = fake_service.calls[-1]
    assert name == "get_concurrency_usage"
    assert kwargs == {}


def test_config_path(invoke):
    result = invoke(["config", "path"], with_key=False)
    assert result.exit_code == 0
    assert "config.toml" in result.stdout
