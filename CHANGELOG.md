# Changelog

All notable changes to the Geonode Scraper CLI will be documented in this file.

The format is inspired by Keep a Changelog.

## [Unreleased]

## [0.2.3] - 2026-10-29

- Removed the internal repository preparation notes and links to the old monorepo.

- Docs links point to the package's page at https://docs.geonode.com/docs/scraper-api/guides/sdks/cli.

- README rewritten so it can be published as the CLI page on docs.geonode.com: configuration table, common tasks, scripting with `--json`, commands and exit codes. Removed the `python -m geonode_scraper_cli` fallback, which does not work (the package has no `__main__`).

## [0.2.2] - 2026-10-21

- The package page links to geonode.com, the Scraper API docs and sign-up.
- README: a sign-up link near the top.

## [0.2.1] - 2026-10-19

- Every request names the CLI: `User-Agent: geonode-cli/<version> geonode-agent-tools/<version> geonode-python-sdk/<version>`.
- Bumped `geonode-scraper-tools-core` dependency to `>=0.5.0`.
- Default host is now the production API, `https://scraper.geonode.io`, instead of
  `http://localhost`. Flags, environment variables and the config file override it as
  before; this only changes what happens when nothing is configured.

## [0.2.0] - 2026-07-15

- Added `search` commands: `search run`, `search jobs list`, `search jobs get`.
- Added `usage concurrency` command to check the caller's live work-concurrency slot usage against their plan limit.
- `map run`'s `--include-subdomains/--no-subdomains` flag now defaults to `--no-subdomains`, matching the API's new default discovery scope.
- Bumped `geonode-scraper-tools-core` dependency to `>=0.4.0`.

## [0.1.0] - 2026-06-23

- Initial release of the `gscraper` command-line interface, built on top of `geonode-scraper-tools-core`.
- Commands: `extract`, `jobs` (get/list/wait), `batch` (create/status/wait/list/cancel), `crawl` (create/status/wait/list/cancel), `map` (run/jobs list/jobs get), `stats`, `health`, and `config` (path/show).
- Human-readable table output by default with `--json` / `--yaml` for machine-readable envelopes.
- Configuration resolved with precedence flag > environment (`GEONODE_SCRAPER_*`) > TOML profile (`~/.config/geonode-scraper/config.toml`) > default.
