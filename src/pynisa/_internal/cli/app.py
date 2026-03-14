"""CLI application for pynisa."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

import pynisa
from pynisa._internal.sources import get_display_name, sources_for_asset
from pynisa._internal.sources.base import RankingResult

app = typer.Typer(
    name="nisa",
    help="Fetch NISA account trading rankings from Japanese brokerages.",
    invoke_without_command=True,
)
console = Console()

# --- Asset type subcommands (nisa us, nisa cn, etc.) ---

_ASSET_TYPES = {
    "us": "US Stocks",
    "cn": "Chinese/HK Stocks",
    "asean": "ASEAN Stocks",
    "jp_etf": "JP ETFs",
    "foreign_etf": "Foreign ETFs",
    "fund": "Investment Trusts",
}


def _make_asset_command(asset_key: str, label: str) -> None:
    @app.command(asset_key, help=f"Fetch NISA {label} rankings.")
    def _cmd(
        source: Optional[str] = typer.Argument(
            None, help="Brokerage name (omit for all sources)"
        ),
        count: int = typer.Option(
            10, "--count", "-n", help="Number of results"
        ),
        format: str = typer.Option(
            "table", "--format", "-f",
            help="Output format: table, csv, json",
        ),
        date: Optional[str] = typer.Option(
            None, "--date", "-d", help="Date (YYYY-MM-DD)"
        ),
        last: int = typer.Option(
            1, "--last", "-l", help="Show last N weeks"
        ),
        live: bool = typer.Option(
            False, "--live", help="Force live fetch (skip DB)"
        ),
    ) -> None:
        pairs = sources_for_asset(asset_key)
        if not pairs:
            console.print(
                f"[yellow]No sources support {label} rankings.[/yellow]"
            )
            raise typer.Exit(0)

        if source:
            pairs = [(s, c) for s, c in pairs if s == source]
            if not pairs:
                console.print(
                    f"[red]Error:[/red] {source!r} does not "
                    f"have {label} rankings."
                )
                raise typer.Exit(1)

        if last > 1:
            for src_name, cat in pairs:
                _print_last_n(
                    src_name, cat, count=count, last=last,
                    format=format,
                )
        elif format != "table" or len(pairs) == 1:
            for src_name, cat in pairs:
                _fetch_and_print(
                    src_name, cat, count, format,
                    date=date, live=live,
                )
        else:
            _print_side_by_side(
                pairs, count=count, date=date, live=live,
            )


for _key, _label in _ASSET_TYPES.items():
    _make_asset_command(_key, _label)


# --- Default command (JP stocks) ---

@app.callback(invoke_without_command=True)
def default(
    ctx: typer.Context,
    last: int = typer.Option(
        1, "--last", "-l", help="Show last N weeks"
    ),
    live: bool = typer.Option(
        False, "--live", help="Force live fetch (skip DB)"
    ),
) -> None:
    """Show default (JP stock) rankings from all sources."""
    if ctx.invoked_subcommand is not None:
        return
    if last > 1:
        for source_name in pynisa.sources():
            _print_last_n(source_name, None, count=10, last=last)
    else:
        _show_all_sources_default(live=live)


def _show_all_sources_default(*, live: bool = False) -> None:
    tables: list[Table] = []
    for source_name in pynisa.sources():
        try:
            result = pynisa.ranking(source_name, live=live)
            tables.append(
                _build_table(result, source=source_name, category=None)
            )
        except Exception as e:
            console.print(f"[red]{source_name}: {e}[/red]")
    if tables:
        _print_grid(tables)


# --- Per-source commands (nisa rakuten, nisa sbi) ---

def _make_source_command(source_name: str) -> None:
    label = get_display_name(source_name)

    @app.command(
        source_name, help=f"Fetch NISA ranking from {label}."
    )
    def _cmd(
        category: Optional[str] = typer.Option(
            None, "--category", "-c", help="Ranking category"
        ),
        count: int = typer.Option(
            10, "--count", "-n", help="Number of results"
        ),
        format: str = typer.Option(
            "table", "--format", "-f",
            help="Output format: table, csv, json",
        ),
        date: Optional[str] = typer.Option(
            None, "--date", "-d", help="Date (YYYY-MM-DD)"
        ),
        last: int = typer.Option(
            1, "--last", "-l", help="Show last N weeks"
        ),
        live: bool = typer.Option(
            False, "--live", help="Force live fetch (skip DB)"
        ),
    ) -> None:
        if last > 1:
            _print_last_n(
                source_name, category, count=count, last=last,
                format=format,
            )
        else:
            _fetch_and_print(
                source_name, category, count, format,
                date=date, live=live,
            )


for _src in pynisa.sources():
    _make_source_command(_src)


# --- Utility commands ---

@app.command("sync")
def sync_cmd(
    force: bool = typer.Option(
        False, "--force", help="Force re-download"
    ),
) -> None:
    """Download or update the ranking database."""
    try:
        pynisa.sync(force=force)
        from pynisa._internal.db.read import read_meta

        updated = read_meta("updated_at") or "unknown"
        console.print(f"[green]Database synced.[/green] Last updated: {updated}")
    except Exception as e:
        console.print(f"[red]Sync failed:[/red] {e}")
        raise typer.Exit(1)


@app.command("dates")
def dates_cmd(
    source: str = typer.Argument(help="Brokerage name"),
    category: Optional[str] = typer.Option(
        None, "--category", "-c", help="Ranking category"
    ),
) -> None:
    """List available dates in the database for a source."""
    available = pynisa.dates(source, category)
    if not available:
        console.print("[yellow]No dates available. Run 'nisa sync' first.[/yellow]")
        raise typer.Exit(0)

    display = get_display_name(source)
    title = f"Available dates — {display}"
    if category:
        title += f" ({category})"

    table = Table(title=title)
    table.add_column("Date", style="cyan")
    for d in available:
        table.add_row(d)
    console.print(table)


@app.command("history")
def history_cmd(
    source: str = typer.Argument(help="Brokerage name"),
    ticker: str = typer.Argument(help="Ticker/code"),
    category: Optional[str] = typer.Option(
        None, "--category", "-c", help="Ranking category"
    ),
    limit: int = typer.Option(
        52, "--limit", "-l", help="Max data points"
    ),
) -> None:
    """Show rank history for a ticker over time."""
    import pandas as pd

    result = pynisa.history(
        source, ticker, category=category, limit=limit
    )
    if result.data.empty:
        console.print("[yellow]No history found.[/yellow]")
        raise typer.Exit(0)

    display = get_display_name(source)
    name = result.data.iloc[0]["name"] if "name" in result.data.columns else ""
    title = f"{display} — {ticker}"
    if name:
        title += f" {name}"
    if category:
        title += f" ({category})"

    table = Table(title=title, show_lines=False)
    table.add_column("date", style="cyan")
    table.add_column("rank", justify="right")
    table.add_column("change")
    if not category and "category" in result.data.columns:
        table.add_column("category", style="dim")

    for _, row in result.data.iterrows():
        change_val = str(row.get("change", ""))
        if change_val in ("↑", "NEW", "New!"):
            change_val = f"[green]{change_val}[/green]"
        elif change_val == "↓":
            change_val = f"[red]{change_val}[/red]"
        elif change_val == "→":
            change_val = f"[dim]{change_val}[/dim]"

        row_vals = [
            str(row["date"]),
            str(row["rank"]) if pd.notna(row["rank"]) else "",
            change_val,
        ]
        if not category and "category" in result.data.columns:
            row_vals.append(str(row["category"]))
        table.add_row(*row_vals)

    console.print(table)


@app.command("categories")
def list_categories(
    source: str = typer.Argument(help="Brokerage name"),
) -> None:
    """List available ranking categories for a source."""
    try:
        cats = pynisa.categories(source)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    table = Table(
        title=f"Categories — {get_display_name(source)}"
    )
    table.add_column("Category", style="cyan")
    for cat in cats:
        table.add_row(cat)
    console.print(table)


@app.command("sources")
def list_sources() -> None:
    """List available brokerage sources."""
    srcs = pynisa.sources()
    table = Table(title="Available Sources")
    table.add_column("Source", style="cyan")
    for s in srcs:
        table.add_row(s)
    console.print(table)


# --- Shared helpers ---

def _fetch_and_print(
    source: str,
    category: str | None,
    count: int,
    format: str,
    *,
    date: str | None = None,
    live: bool = False,
) -> None:
    try:
        result = pynisa.ranking(
            source, category, count=count, date=date, live=live
        )
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Failed to fetch data:[/red] {e}")
        raise typer.Exit(1)

    if result.data.empty:
        console.print("[yellow]No data available.[/yellow]")
        raise typer.Exit(0)

    if format == "csv":
        console.print(result.data.to_csv(index=False))
    elif format == "json":
        console.print(
            result.data.to_json(
                orient="records", force_ascii=False, indent=2
            )
        )
    else:
        _print_table(result, source=source, category=category)


def _print_last_n(
    source: str,
    category: str | None,
    *,
    count: int = 10,
    last: int = 4,
    format: str = "table",
) -> None:
    """Print the last N weeks of rankings, latest first.

    Displays tables side-by-side in pairs (2 per row).
    """
    from pynisa._internal.sources import get_source

    src = get_source(source)
    resolved_cat = category or src._config.get("default_category", "")
    available = pynisa.dates(source, resolved_cat)

    if not available:
        console.print(
            "[yellow]No historical data. Run 'nisa sync' first.[/yellow]"
        )
        return

    dates_to_show = available[:last]
    tables: list[Table] = []

    for d in dates_to_show:
        try:
            result = pynisa.ranking(
                source, category, count=count, date=d
            )
            tables.append(
                _build_table(result, source=source, category=category)
            )
        except Exception as e:
            console.print(f"[red]{source} ({d}): {e}[/red]")

    if not tables:
        return

    if format != "table":
        # For csv/json, just print sequentially
        for d in dates_to_show:
            try:
                result = pynisa.ranking(
                    source, category, count=count, date=d
                )
                if format == "csv":
                    console.print(result.data.to_csv(index=False))
                elif format == "json":
                    console.print(
                        result.data.to_json(
                            orient="records",
                            force_ascii=False,
                            indent=2,
                        )
                    )
            except Exception:
                pass
        return

    # Print in pairs (2 per row)
    for i in range(0, len(tables), 2):
        pair = tables[i:i + 2]
        grid = Table.grid(padding=(0, 3))
        for _ in pair:
            grid.add_column()
        grid.add_row(*pair)
        console.print(grid)
        if i + 2 < len(tables):
            console.print()


def _print_side_by_side(
    pairs: list[tuple[str, str]],
    *,
    count: int = 10,
    date: str | None = None,
    live: bool = False,
) -> None:
    """Print multiple source/category tables side by side."""
    tables: list[Table] = []
    for src_name, cat in pairs:
        try:
            result = pynisa.ranking(
                src_name, cat, count=count, date=date, live=live
            )
            tables.append(
                _build_table(result, source=src_name, category=None)
            )
        except Exception as e:
            console.print(f"[red]{src_name}: {e}[/red]")
    if tables:
        _print_grid(tables)


def _print_grid(tables: list[Table]) -> None:
    """Render tables side-by-side in a grid."""
    grid = Table.grid(padding=(0, 3))
    for _ in tables:
        grid.add_column()
    grid.add_row(*tables)
    console.print(grid)


def _build_table(
    result: RankingResult, *, source: str, category: str | None
) -> Table:
    """Build a rich Table from a RankingResult."""
    import pandas as pd

    df = result.data
    period = result.period or result.updated or ""
    display = get_display_name(source)
    title = f"{display} ({period})" if period else display
    if category:
        title += f" — {category}"

    table = Table(title=title, show_lines=False)

    hidden = {
        "source", "detail_url", "category",
        "sector", "market", "date",
    }
    display_cols = [c for c in df.columns if c not in hidden]

    for col in display_cols:
        justify = "right" if col == "rank" else "left"
        table.add_column(col, justify=justify)

    for _, row in df.iterrows():
        values: list[str] = []
        for col in display_cols:
            val = str(row[col]) if pd.notna(row[col]) else ""
            if col == "change":
                if val in ("↑", "NEW", "New!"):
                    val = f"[green]{val}[/green]"
                elif val == "↓":
                    val = f"[red]{val}[/red]"
                elif val == "→":
                    val = f"[dim]{val}[/dim]"
            values.append(val)
        table.add_row(*values)

    return table


def _print_table(
    result: RankingResult, *, source: str, category: str | None
) -> None:
    """Render RankingResult as a rich table."""
    console.print(_build_table(result, source=source, category=category))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
