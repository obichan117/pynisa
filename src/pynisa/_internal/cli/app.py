"""CLI application for pynisa."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

import pynisa
from pynisa._internal.sources import sources_for_asset
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
        count: int = typer.Option(10, "--count", "-n", help="Number of results"),
        format: str = typer.Option(
            "table", "--format", "-f", help="Output format: table, csv, json"
        ),
    ) -> None:
        pairs = sources_for_asset(asset_key)
        if not pairs:
            console.print(f"[yellow]No sources support {label} rankings.[/yellow]")
            raise typer.Exit(0)

        if source:
            # Filter to specific source
            pairs = [(s, c) for s, c in pairs if s == source]
            if not pairs:
                console.print(
                    f"[red]Error:[/red] {source!r} does not have {label} rankings."
                )
                raise typer.Exit(1)

        if format != "table" or len(pairs) == 1:
            for src_name, cat in pairs:
                _fetch_and_print(src_name, cat, count, format)
        else:
            # Side by side
            tables: list[Table] = []
            for src_name, cat in pairs:
                try:
                    result = pynisa.ranking(src_name, cat, count=count)
                    tables.append(
                        _build_table(result, source=src_name, category=None)
                    )
                except Exception as e:
                    console.print(f"[red]{src_name}: {e}[/red]")
            if tables:
                grid = Table.grid(padding=(0, 3))
                for _ in tables:
                    grid.add_column()
                grid.add_row(*tables)
                console.print(grid)


for _key, _label in _ASSET_TYPES.items():
    _make_asset_command(_key, _label)


# --- Default command (JP stocks) ---

@app.callback(invoke_without_command=True)
def default(ctx: typer.Context) -> None:
    """Show default (JP stock) rankings from all sources."""
    if ctx.invoked_subcommand is not None:
        return
    _show_all_sources_default()


def _show_all_sources_default() -> None:
    tables: list[Table] = []
    for source_name in pynisa.sources():
        try:
            result = pynisa.ranking(source_name)
            tables.append(_build_table(result, source=source_name, category=None))
        except Exception as e:
            console.print(f"[red]{source_name}: {e}[/red]")
    if tables:
        grid = Table.grid(padding=(0, 3))
        for _ in tables:
            grid.add_column()
        grid.add_row(*tables)
        console.print(grid)


# --- Per-source commands (nisa rakuten, nisa sbi) ---

def _make_source_command(source_name: str) -> None:
    @app.command(source_name, help=f"Fetch NISA ranking from {source_name.capitalize()}.")
    def _cmd(
        category: Optional[str] = typer.Option(
            None, "--category", "-c", help="Ranking category"
        ),
        count: int = typer.Option(10, "--count", "-n", help="Number of results"),
        format: str = typer.Option(
            "table", "--format", "-f", help="Output format: table, csv, json"
        ),
    ) -> None:
        _fetch_and_print(source_name, category, count, format)


for _src in pynisa.sources():
    _make_source_command(_src)


# --- Utility commands ---

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

    table = Table(title=f"Categories — {source.capitalize()}")
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
    source: str, category: str | None, count: int, format: str
) -> None:
    try:
        result = pynisa.ranking(source, category, count=count)
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
            result.data.to_json(orient="records", force_ascii=False, indent=2)
        )
    else:
        _print_table(result, source=source, category=category)


def _build_table(
    result: RankingResult, *, source: str, category: str | None
) -> Table:
    """Build a rich Table from a RankingResult."""
    import pandas as pd

    df = result.data
    period = result.period or result.updated or ""
    title = f"{source.capitalize()} ({period})" if period else source.capitalize()
    if category:
        title += f" — {category}"

    table = Table(title=title, show_lines=False)

    display_cols = [
        c for c in df.columns if c not in ("source", "detail_url", "category")
    ]

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
