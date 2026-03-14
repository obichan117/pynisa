# pynisa

Fetch NISA account trading rankings from major Japanese securities brokerages.

## Quick Start

```bash
uv sync                          # Install dependencies
uv run pytest --tb=short         # Run tests
uv run mkdocs build --strict     # Build docs
uv run mkdocs serve              # Preview docs
uv run nisa ranking rakuten      # Test CLI
```

## Architecture

```
src/pynisa/
├── __init__.py                  # Public API: ranking(), categories(), sources()
└── _internal/
    ├── core/
    │   ├── fetch.py             # HTTP layer (I/O only, returns raw text)
    │   └── parse.py             # CSV/HTML parse helpers (no I/O)
    ├── sources/
    │   ├── __init__.py          # Source registry + get_source() factory
    │   ├── base.py              # NisaSource ABC
    │   ├── rakuten.py + .yaml   # Rakuten (CSV endpoints)
    │   └── sbi.py + .yaml       # SBI (HTML scraping)
    └── cli/
        └── app.py               # Typer CLI: nisa ranking/sources/categories
```

## Adding a New Source

1. Create `src/pynisa/_internal/sources/<name>.py` and `<name>.yaml`
2. Subclass `NisaSource`, implement `name`, `categories()`, `fetch_ranking()`
3. Call `_register("<name>", YourSourceClass)` at module level
4. Add import to `sources/__init__.py` `_auto_register()`

## Key Design Decisions

- **Fetch vs Parse separation**: `core/fetch.py` does HTTP, `core/parse.py` transforms text. Source modules orchestrate both.
- **Config in YAML**: URLs, selectors, column names live in `.yaml` files co-located with source modules.
- **`_internal/` pattern**: Only `pynisa.ranking()`, `pynisa.categories()`, `pynisa.sources()` are public API.

## Data Sources

- **Rakuten**: 12 public CSV files at `rakuten-sec.co.jp/web/market/ranking/nisa/`
- **SBI**: Server-rendered HTML via ETGate (Shift-JIS encoded)
- Research docs in `docs/research/`
