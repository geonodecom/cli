![Geonode CLI: Web Scraping, Crawling & Search](assets/banner.svg)

# Geonode CLI: Web Scraping, Crawling & Search

Collect web data from your terminal for scripts, agents and data pipelines. Extract pages, crawl sites, discover URLs, search the web and run batches with the Geonode CLI. JSON output and exit codes make the results easy to use in your own automation.

**[Try Geonode for free](https://app.geonode.com/sign-up)**

[Integrations page](https://geonode.com/integrations) · [Geonode API docs](https://docs.geonode.com/docs/scraper-api) · [CLI setup guide](https://docs.geonode.com/docs/scraper-api/guides/sdks/cli) · [View package on PyPI](https://pypi.org/project/geonode-scraper-cli/) · [View source on GitHub](https://github.com/geonodecom/cli) · [Complete guide](docs/guide.md)

<!-- BEGIN README NAV -->
[Quick start](#quick-start) · [Choose a command](#choose-a-command) · [Example: save a page for a scheduled pipeline](#example-save-a-page-for-a-scheduled-pipeline) · [Setup questions](#setup-questions)
<!-- END README NAV -->

## Workflow ideas

- **Schedule a content refresh.** Run extraction commands from your scheduler, inspect exit codes, and save JSON results.
- **Inspect a site from the terminal.** Map URLs, select pages and extract Markdown without writing an API client.

## Quick start

Requires Python 3.10 or newer and a Geonode API key from the [dashboard](https://app.geonode.com/).

```sh
pipx install geonode-scraper-cli
export GEONODE_SCRAPER_API_KEY="your-api-key"
gscraper extract https://example.com --format markdown
```

Use `pip install geonode-scraper-cli` if you already manage your own virtual environment. On Windows PowerShell, set `$env:GEONODE_SCRAPER_API_KEY = "your-api-key"`.

For machine-readable output:

```sh
gscraper extract https://example.com --format markdown --json
```

A successful response has `ok: true` and the API result under `result`; a failed request has `ok: false` and an `error` object. API requests require an active account and use your plan's allowance.

## Choose a command

| Task | Command |
| --- | --- |
| Extract a page | `gscraper extract URL --format markdown` |
| Extract several URLs | `gscraper batch create URL [URL ...]` |
| Crawl a website | `gscraper crawl create URL --depth 2 --limit 50` |
| Discover URLs | `gscraper map run URL` |
| Search the web | `gscraper search run "your query"` |
| Wait for a job | `gscraper jobs wait JOB_ID` |
| Check concurrency | `gscraper usage concurrency` |

Use `gscraper --help` or `gscraper COMMAND --help` for options. See the [complete guide](docs/guide.md) for background jobs, profiles, output files, shell completion and exit codes.

## Configuration and errors

Set credentials through the environment or a local config file; command-line keys can remain in shell history. `gscraper config show` masks keys. Flags override environment variables, which override the selected profile.

A missing/invalid key or blocked target exits with code `4`; invalid request/extraction failure uses `6`, a network failure uses `7`, and a wait timeout uses `8`. See [all exit codes](docs/guide.md#exit-codes) when handling failures in scripts.

<!-- BEGIN SHARED WORKFLOW GUIDE -->
## Example: save a page for a scheduled pipeline

After configuring GEONODE_SCRAPER_API_KEY, run one extraction and save its structured response. This Bash example writes to a local file; it does not create a scheduler or a storage service.

```sh
if gscraper extract https://example.com --format markdown --json > page-result.json; then
  echo "Inspect ok and result.data.markdown in page-result.json"
else
  echo "Extraction failed; inspect page-result.json" >&2
fi
```

**Expected result:** Successful synchronous JSON output has ok: true and content under result.data.markdown. Inspect failure output before importing it into a dataset.

## Setup questions

Command not found? Check that the environment where you installed the package is active and that its Scripts or bin directory is on PATH. pipx manages a separate command environment.

Wrong account or endpoint? Inspect gscraper config show, which masks keys. Flags override environment variables, which override the selected configuration profile.

Need reliable scheduling? Let your scheduler inspect the command's exit code, preserve failed output and apply a bounded retry policy. A submitted background job still needs a completion check.

Does the CLI run an MCP server? No. It calls the Geonode API; the hosted MCP endpoint is a separate assistant connection.

These recipes describe source-supported workflows. They have not been run as authenticated end-to-end examples in this review.
<!-- END SHARED WORKFLOW GUIDE -->

## Development and support

See [CONTRIBUTING.md](CONTRIBUTING.md) for local checks and releases.

For API or account questions, [contact Geonode](https://geonode.com/contact). For security issues, follow [SECURITY.md](SECURITY.md). Licensed under [MIT](LICENSE).

**[Try Geonode for free](https://app.geonode.com/sign-up)**
