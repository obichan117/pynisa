"""Database read operations. Used by the public API."""

from __future__ import annotations

import sqlite3

import pandas as pd

from pynisa._internal.db.core import db_exists, get_connection


def read_ranking(
    source: str,
    category: str,
    *,
    date: str | None = None,
    count: int = 10,
) -> pd.DataFrame | None:
    """Read ranking from the database.

    Parameters
    ----------
    source : str
        Brokerage name.
    category : str
        Ranking category.
    date : str, optional
        Date string (YYYY-MM-DD). If None, returns the latest available.
    count : int
        Maximum number of rows.

    Returns
    -------
    pd.DataFrame or None
        DataFrame with ranking data, or None if not found.
    """
    if not db_exists():
        return None

    try:
        conn = get_connection(readonly=True)
    except sqlite3.OperationalError:
        return None

    try:
        if date is None:
            row = conn.execute(
                "SELECT MAX(date) FROM rankings WHERE source = ? AND category = ?",
                (source, category),
            ).fetchone()
            if row is None or row[0] is None:
                return None
            date = row[0]

        rows = conn.execute(
            """\
            SELECT rank, change, ticker, name, sector, market, detail_url
            FROM rankings
            WHERE source = ? AND category = ? AND date = ?
            ORDER BY rank
            LIMIT ?
            """,
            (source, category, date, count),
        ).fetchall()

        if not rows:
            return None

        df = pd.DataFrame([dict(r) for r in rows])
        # Drop empty optional columns
        for col in ("sector", "market", "detail_url"):
            if col in df.columns and (df[col] == "").all():
                df = df.drop(columns=[col])
        df["source"] = source
        df["category"] = category
        df["date"] = date
        return df
    finally:
        conn.close()


def read_ranking_dates(
    source: str,
    category: str | None = None,
) -> list[str]:
    """Return available dates for a source (and optionally category).

    Returns dates in descending order (newest first).
    """
    if not db_exists():
        return []

    try:
        conn = get_connection(readonly=True)
    except sqlite3.OperationalError:
        return []

    try:
        if category:
            rows = conn.execute(
                """\
                SELECT DISTINCT date FROM rankings
                WHERE source = ? AND category = ?
                ORDER BY date DESC
                """,
                (source, category),
            ).fetchall()
        else:
            rows = conn.execute(
                """\
                SELECT DISTINCT date FROM rankings
                WHERE source = ?
                ORDER BY date DESC
                """,
                (source,),
            ).fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()


def read_history(
    source: str,
    ticker: str,
    *,
    category: str | None = None,
    limit: int = 52,
) -> pd.DataFrame:
    """Return rank history for a ticker over time.

    Parameters
    ----------
    source : str
        Brokerage name.
    ticker : str
        Ticker/code to look up.
    category : str, optional
        Filter to a specific category. If None, uses the source default.
    limit : int
        Maximum number of weeks to return.

    Returns
    -------
    pd.DataFrame
        Columns: date, rank, change, category, name.
    """
    if not db_exists():
        return pd.DataFrame(columns=["date", "rank", "change", "category", "name"])

    try:
        conn = get_connection(readonly=True)
    except sqlite3.OperationalError:
        return pd.DataFrame(columns=["date", "rank", "change", "category", "name"])

    try:
        if category:
            rows = conn.execute(
                """\
                SELECT date, rank, change, category, name
                FROM rankings
                WHERE source = ? AND ticker = ? AND category = ?
                ORDER BY date DESC
                LIMIT ?
                """,
                (source, ticker, category, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """\
                SELECT date, rank, change, category, name
                FROM rankings
                WHERE source = ? AND ticker = ?
                ORDER BY date DESC
                LIMIT ?
                """,
                (source, ticker, limit),
            ).fetchall()
        return pd.DataFrame([dict(r) for r in rows])
    finally:
        conn.close()


def read_meta(key: str) -> str | None:
    """Read a metadata value by key."""
    if not db_exists():
        return None

    try:
        conn = get_connection(readonly=True)
    except sqlite3.OperationalError:
        return None

    try:
        row = conn.execute(
            "SELECT value FROM meta WHERE key = ?", (key,)
        ).fetchone()
        return row[0] if row else None
    finally:
        conn.close()
