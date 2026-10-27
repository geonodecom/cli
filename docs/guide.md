# Geonode Scraper CLI

[Integrations page](https://geonode.com/integrations) · [Geonode API docs](https://docs.geonode.com/docs/scraper-api) · [CLI setup guide](https://docs.geonode.com/docs/scraper-api/guides/sdks/cli) · [GitHub source](https://github.com/geonodecom/cli) · [Published package](https://pypi.org/project/geonode-scraper-cli/) · [Repository overview](../README.md)

**[Try Geonode for free](https://app.geonode.com/sign-up)**

`gscraper` brings the [Geonode Scraper API](https://geonode.com/products/scraper-api) to your terminal and scripts: extract a page as Markdown or HTML, run batches and crawls, map a site's URLs, search the web and check usage. Package: [`geonode-scraper-cli` on PyPI](https://pypi.org/project/geonode-scraper-cli/).

## Before you start

- Python 3.10 or newer, on Linux, macOS or Windows.
- A Geonode API key. Sign in to the [Geonode dashboard](https://app.geonode.com/), open **API Keys**, and create a key or copy an existing one.

## Install

With [pipx](https://pipx.pypa.io), which keeps the CLI in its own environment and puts `gscraper` on your `PATH`:

```sh
pipx install geonode-scraper-cli
```

Or with pip:

```sh
pip install geonode-scraper-cli
```

On Windows, pip puts `gscraper` in Python's `Scripts` folder. If the command isn't found, add that folder to your `PATH`, or use pipx, which does it for you.

## Configure

Set your key in an environment variable. On Linux and macOS:

```sh
export GEONODE_SCRAPER_API_KEY="your-api-key"
```

On Windows PowerShell: `$env:GEONODE_SCRAPER_API_KEY = "your-api-key"`.

The CLI calls the production API, `https://scraper.geonode.io`, unless you set another host. You can also keep settings in a config file, `~/.config/geonode-scraper/config.toml`, with one section per profile:

```toml
[default]
api_key = "your-api-key"

[team]
api_key = "another-api-key"
```

Pick a profile with `--profile team` or `GEONODE_SCRAPER_PROFILE=team`. `gscraper config path` prints where the file is, and `gscraper config show` prints the active settings with keys masked.

| Setting | Flag | Environment variable | Config key | Default |
|---|---|---|---|---|
| API key | `--api-key` | `GEONODE_SCRAPER_API_KEY` | `api_key` | none |
| API host | `--host` | `GEONODE_SCRAPER_HOST` | `host` | `https://scraper.geonode.io` |
| Request timeout, seconds | `--timeout` | `GEONODE_SCRAPER_TIMEOUT` | `timeout` | none |
| Check TLS certificates | `--verify-ssl` / `--no-verify-ssl` | `GEONODE_SCRAPER_VERIFY_SSL` | `verify_ssl` | on |
| Profile | `--profile` | `GEONODE_SCRAPER_PROFILE` | — | `default` |
| Config file | — | `GEONODE_SCRAPER_CONFIG` | — | `~/.config/geonode-scraper/config.toml` |

A flag beats the environment, the environment beats the config file. Keep the key out of `--api-key` when you can: the flag stays in your shell history.

## Your first command

```sh
gscraper extract https://example.com --format markdown
```

## Common tasks

Render JavaScript, pick a country, wait for an element, and save the page to a file:

```sh
gscraper extract https://example.com/products --format markdown --render-js --proxy-country DE --wait-for "#content" --output products.md
```

Run an extraction in the background and wait for it:

```sh
gscraper extract https://example.com --async
gscraper jobs wait JOB_ID
```

Extract many URLs at once, then wait for the batch:

```sh
gscraper batch create https://example.com https://example.org --format markdown
gscraper batch wait JOB_ID
```

Crawl a site up to a depth and a page limit:

```sh
gscraper crawl create https://example.com --depth 2 --limit 50 --format markdown
gscraper crawl wait JOB_ID
```

List a site's URLs, keeping only those that contain a word:

```sh
gscraper map run https://example.com --search pricing
```

Search the web:

```sh
gscraper search run "geonode scraper api" --locale en
```

Check usage:

```sh
gscraper usage concurrency
gscraper stats --start-date 2026-10-01
```

## Output and scripting

Commands print a readable summary. Add `--json` or `--yaml` to print the full result instead, before or after the command name:

```sh
gscraper extract https://example.com --format markdown --json | jq -r .result.data.markdown
```

The JSON is `{"ok": true, "operation": "...", "result": {...}}` on success and `{"ok": false, "operation": "...", "error": {...}}` on failure. `error` carries the API's HTTP `status`, a `code`, a `message` and `retryable`.

## Commands

```text
gscraper extract URL [--format markdown|html] [--render-js] [--async] [--proxy-country US]
                     [--proxy-type residential|datacenter|mix] [--header "K: V"]
                     [--wait-for SELECTOR] [--wait-until load|networkidle|...] [--wait-timeout MS]
                     [--output FILE]

gscraper jobs get JOB_ID
gscraper jobs list [--status completed] [--url ...] [--page N]
gscraper jobs wait JOB_ID [--timeout S] [--interval S]

gscraper batch create URL [URL ...] [--format markdown] [--render-js] [--proxy-country US]
gscraper batch status JOB_ID
gscraper batch wait JOB_ID [--timeout S] [--interval S]
gscraper batch list [--status ...]
gscraper batch cancel JOB_ID

gscraper crawl create URL [--depth 2] [--limit 50] [--include-subdomains] [--all-domains]
gscraper crawl status JOB_ID
gscraper crawl wait JOB_ID
gscraper crawl list [--url ...]
gscraper crawl cancel JOB_ID

gscraper map run URL [--search TERM] [--include-subdomains] [--keep-query]
gscraper map jobs list
gscraper map jobs get JOB_ID

gscraper search run QUERY [--locale en] [--page 1] [--safe off|moderate|strict] [--time-range day|week|month|year]
gscraper search jobs list [--query ...] [--status completed]
gscraper search jobs get JOB_ID

gscraper stats [--start-date ISO] [--end-date ISO]
gscraper usage concurrency
gscraper health
gscraper config path | show
```

`gscraper --help` and `gscraper COMMAND --help` show every option.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Any other error, including 402, 429 and 5xx |
| 2 | Wrong command or arguments |
| 4 | The key is missing or wrong (401), or the target is blocked (403) |
| 5 | Not found (404) |
| 6 | Invalid request, or the page could not be extracted (422) |
| 7 | No response from the API: network or connection problem |
| 8 | A `wait` command ran out of time |

## Shell completion

```sh
gscraper --install-completion
```

## Versions and support

- The latest version is on [PyPI](https://pypi.org/project/geonode-scraper-cli/). `gscraper --version` prints yours.
- Requests send `User-Agent: geonode-cli/<version>`, which helps support see which version you use.
- Questions or problems: [contact Geonode](https://geonode.com/contact).
