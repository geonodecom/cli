# CLI: workflow recipes and output guide

[Repository overview](../README.md) · [Geonode documentation](https://pypi.org/project/geonode-scraper-cli/)

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

Source-reviewed recipes; authenticated workflow execution has not been tested in this review.
