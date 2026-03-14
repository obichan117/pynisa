"""Database write operations. Used by the pipeline only."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

import pandas as pd


def insert_rankings(
    conn: sqlite3.Connection,
    source: str,
    category: str,
    date: str,
    df: pd.DataFrame,
) -> int:
    """Insert ranking rows for a given source/category/date.

    Skips rows that already exist (INSERT OR IGNORE).

    Returns
    -------
    int
        Number of rows inserted.
    """
    rows = []
    for _, row in df.iterrows():
        rank_val = row.get("rank", 0)
        if pd.isna(rank_val):
            continue  # skip rows with no rank
        rows.append((
            source,
            category,
            date,
            int(rank_val),
            str(row.get("change", "")),
            str(row.get("ticker", "")),
            str(row.get("name", "")),
            str(row.get("sector", "")),
            str(row.get("market", "")),
            str(row.get("detail_url", "")),
        ))

    cursor = conn.executemany(
        """\
        INSERT OR IGNORE INTO rankings
            (source, category, date, rank, change, ticker, name,
             sector, market, detail_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    return cursor.rowcount


def update_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    """Insert or update a metadata key-value pair."""
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        (key, value),
    )
    conn.commit()


def set_updated_at(conn: sqlite3.Connection) -> None:
    """Set the 'updated_at' metadata to current UTC time."""
    now = datetime.now(timezone.utc).isoformat()
    update_meta(conn, "updated_at", now)
