"""SQLite database core: schema initialization and connection management."""

from __future__ import annotations

import sqlite3
from pathlib import Path

_DEFAULT_DB_DIR = Path.home() / ".cache" / "pynisa"
_DEFAULT_DB_NAME = "nisa.db"

_SCHEMA_SQL = """\
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rankings (
    source     TEXT    NOT NULL,
    category   TEXT    NOT NULL,
    date       TEXT    NOT NULL,
    rank       INTEGER NOT NULL,
    change     TEXT    NOT NULL DEFAULT '',
    ticker     TEXT    NOT NULL DEFAULT '',
    name       TEXT    NOT NULL DEFAULT '',
    sector     TEXT    NOT NULL DEFAULT '',
    market     TEXT    NOT NULL DEFAULT '',
    detail_url TEXT    NOT NULL DEFAULT '',
    PRIMARY KEY (source, category, date, rank)
);

CREATE INDEX IF NOT EXISTS idx_rankings_lookup
    ON rankings (source, category, date);

CREATE INDEX IF NOT EXISTS idx_rankings_ticker
    ON rankings (ticker, source);
"""


def db_path() -> Path:
    """Return the default database file path."""
    return _DEFAULT_DB_DIR / _DEFAULT_DB_NAME


def db_exists() -> bool:
    """Return True if the database file exists."""
    return db_path().is_file()


def get_connection(
    *, path: Path | None = None, readonly: bool = True
) -> sqlite3.Connection:
    """Open a SQLite connection.

    Parameters
    ----------
    path : Path, optional
        Database file path. Defaults to ``~/.cache/pynisa/nisa.db``.
    readonly : bool
        If True, open in read-only mode.
    """
    p = path or db_path()
    if readonly:
        uri = f"file:{p}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
    else:
        p.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Create tables and indexes if they don't exist."""
    conn.executescript(_SCHEMA_SQL)
