# pynisa

Fetch NISA account trading rankings from major Japanese securities brokerages.

## Quick Start

```bash
uv sync                          # Install dependencies
uv run pytest --tb=short         # Run tests
uv run mkdocs build --strict     # Build docs
uv run mkdocs serve              # Preview docs
uv run nisa rakuten              # Test CLI
uv run nisa --last 4             # Historical (requires DB)
uv run nisa sync                 # Download/update DB
```

## Architecture

```
src/pynisa/
├── __init__.py                  # Public API: ranking(), categories(), sources(),
│                                #   dates(), history(), sync()
└── _internal/
    ├── core/
    │   ├── fetch.py             # HTTP layer (I/O only, returns raw text)
    │   └── parse.py             # CSV parse helpers (no I/O)
    ├── db/
    │   ├── core.py              # SQLite schema, connection management
    │   ├── read.py              # Query rankings, dates, history
    │   └── write.py             # Insert rankings (pipeline only)
    ├── sources/
    │   ├── __init__.py          # Source registry + get_source() factory
    │   ├── base.py              # NisaSource ABC
    │   ├── rakuten.py + .yaml   # Rakuten (CSV endpoints)
    │   └── sbi.py + .yaml       # SBI (HTML scraping)
    ├── cli/
    │   └── app.py               # Typer CLI
    ├── sync.py                  # Download DB from GitHub Releases
    ├── pipeline.py              # Fetch all sources → write to DB
    └── pipeline_cli.py          # CLI entry point for GitHub Actions

.github/workflows/
└── weekly-ranking.yml           # Cron: Mon + 3rd of month → snapshot
```

## Data Flow

1. **GitHub Actions** runs `pipeline.py` on schedule → fetches all rankings → writes to SQLite
2. **SQLite DB** uploaded to GitHub Releases as `db-latest/nisa.db`
3. **Users**: `pynisa.ranking()` auto-downloads DB on first use → DB-first, live-fallback
4. **`--live` flag** or `live=True` skips DB entirely for fresh web fetch

## Adding a New Source

1. Create `src/pynisa/_internal/sources/<name>.py` and `<name>.yaml`
2. Subclass `NisaSource`, implement `name`, `display_name`, `categories()`, `asset_types()`, `fetch_ranking()`
3. Call `_register("<name>", YourSourceClass)` at module level
4. Add import to `sources/__init__.py` `_auto_register()`

## Key Design Decisions

- **Fetch vs Parse separation**: `core/fetch.py` does HTTP, `core/parse.py` transforms text. Source modules orchestrate both.
- **Config in YAML**: URLs, selectors, column names, display names live in `.yaml` files co-located with source modules.
- **`_internal/` pattern**: Only top-level functions in `__init__.py` are public API.
- **DB-first, live-fallback**: Auto-sync DB on first use, fall through to live HTTP if DB unavailable.
- **Display names**: `display_name` in YAML (e.g. "楽天", "SBI") used in CLI output instead of raw identifiers.

## Data Sources

- **Rakuten**: 12 public CSV files — updated **monthly** (~2nd of month)
- **SBI**: Server-rendered HTML via ETGate (Shift-JIS) — updated **weekly**
- Research docs in `docs/research/`
