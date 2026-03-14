"""Shared CLI formatting helpers."""

from __future__ import annotations

import pandas as pd
from rich.console import Console
from rich.table import Table

from pynisa._internal.sources import get_display_name
from pynisa._internal.sources.base import RankingResult

console = Console()


def format_change(val: str) -> str:
    """Apply Rich color markup to a change indicator."""
    if val in ("↑", "NEW", "New!"):
        return f"[green]{val}[/green]"
    if val == "↓":
        return f"[red]{val}[/red]"
    if val == "→":
        return f"[dim]{val}[/dim]"
    return val


def build_table(
    result: RankingResult, *, source: str, category: str | None
) -> Table:
    """Build a rich Table from a RankingResult."""
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
                val = format_change(val)
            values.append(val)
        table.add_row(*values)

    return table


def print_grid(tables: list[Table]) -> None:
    """Render tables side-by-side in a grid."""
    grid = Table.grid(padding=(0, 3))
    for _ in tables:
        grid.add_column()
    grid.add_row(*tables)
    console.print(grid)
