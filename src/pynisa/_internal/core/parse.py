"""Parse helpers. No I/O — operates on raw text only."""

from __future__ import annotations

import io

import pandas as pd
from bs4 import BeautifulSoup, Tag


def parse_csv(
    text: str,
    *,
    columns: list[str],
    skip_footer: int = 0,
) -> pd.DataFrame:
    """Parse CSV text into a DataFrame.

    Parameters
    ----------
    text : str
        Raw CSV content.
    columns : list[str]
        Column names to assign.
    skip_footer : int
        Number of trailing rows to drop (e.g. metadata rows).

    Returns
    -------
    pd.DataFrame
    """
    df = pd.read_csv(
        io.StringIO(text),
        header=None,
        names=columns,
        dtype=str,
    )
    if skip_footer > 0:
        df = df.iloc[:-skip_footer]
    # Convert rank to int where possible
    if "rank" in df.columns:
        df["rank"] = pd.to_numeric(df["rank"], errors="coerce").astype("Int64")
    return df


def parse_html_table(
    html: str,
    *,
    selector: str,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """Extract data from an HTML table matching a CSS selector.

    Parameters
    ----------
    html : str
        Raw HTML content.
    selector : str
        CSS selector for the target ``<table>`` element.
    columns : list[str], optional
        Column names. If None, uses the first ``<tr>`` as header.

    Returns
    -------
    pd.DataFrame
    """
    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one(selector)
    if table is None:
        return pd.DataFrame(columns=columns or [])

    rows: list[list[str]] = []
    for tr in table.select("tr"):
        cells = tr.select("td, th")
        if cells:
            rows.append([_cell_text(c) for c in cells])

    if not rows:
        return pd.DataFrame(columns=columns or [])

    if columns is not None:
        df = pd.DataFrame(rows, columns=columns[: len(rows[0])])
    else:
        df = pd.DataFrame(rows[1:], columns=rows[0])
    return df


def _cell_text(cell: Tag) -> str:
    """Extract cleaned text from a table cell."""
    return cell.get_text(strip=True)
