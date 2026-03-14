"""Tests for database layer."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from pynisa._internal.db.core import get_connection, init_schema
from pynisa._internal.db.read import (
    read_history,
    read_meta,
    read_ranking,
    read_ranking_dates,
)
from pynisa._internal.db.write import (
    insert_rankings,
    set_updated_at,
    update_meta,
)


@pytest.fixture
def db_conn(tmp_path: Path) -> sqlite3.Connection:
    """Create an in-memory-like temp DB with schema initialized."""
    db_file = tmp_path / "test.db"
    conn = get_connection(path=db_file, readonly=False)
    init_schema(conn)
    return conn


@pytest.fixture
def db_path_with_data(tmp_path: Path) -> Path:
    """Create a temp DB populated with sample data."""
    db_file = tmp_path / "test.db"
    conn = get_connection(path=db_file, readonly=False)
    init_schema(conn)

    df = pd.DataFrame({
        "rank": [1, 2, 3],
        "change": ["↑", "↓", "→"],
        "ticker": ["7974", "9432", "8306"],
        "name": ["任天堂", "NTT", "三菱UFJ"],
    })
    insert_rankings(conn, "rakuten", "jp_stock_buy", "2026-02-28", df)

    df2 = pd.DataFrame({
        "rank": [1, 2, 3],
        "change": ["→", "↑", "↓"],
        "ticker": ["8306", "7974", "9432"],
        "name": ["三菱UFJ", "任天堂", "NTT"],
    })
    insert_rankings(conn, "rakuten", "jp_stock_buy", "2026-03-07", df2)
    conn.close()
    return db_file


class TestDbWrite:
    def test_insert_rankings(self, db_conn: sqlite3.Connection) -> None:
        df = pd.DataFrame({
            "rank": [1, 2],
            "change": ["↑", "↓"],
            "ticker": ["7974", "9432"],
            "name": ["任天堂", "NTT"],
        })
        n = insert_rankings(db_conn, "rakuten", "jp_stock_buy", "2026-02-28", df)
        assert n == 2

    def test_insert_duplicate_ignored(
        self, db_conn: sqlite3.Connection
    ) -> None:
        df = pd.DataFrame({
            "rank": [1],
            "change": ["↑"],
            "ticker": ["7974"],
            "name": ["任天堂"],
        })
        insert_rankings(db_conn, "rakuten", "jp_stock_buy", "2026-02-28", df)
        n = insert_rankings(
            db_conn, "rakuten", "jp_stock_buy", "2026-02-28", df
        )
        assert n == 0

    def test_update_meta(self, db_conn: sqlite3.Connection) -> None:
        update_meta(db_conn, "version", "1")
        row = db_conn.execute(
            "SELECT value FROM meta WHERE key = 'version'"
        ).fetchone()
        assert row[0] == "1"

    def test_set_updated_at(self, db_conn: sqlite3.Connection) -> None:
        set_updated_at(db_conn)
        row = db_conn.execute(
            "SELECT value FROM meta WHERE key = 'updated_at'"
        ).fetchone()
        assert row is not None
        assert "T" in row[0]  # ISO format


class TestDbRead:
    def test_read_ranking(
        self, db_path_with_data: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "pynisa._internal.db.read.db_exists", lambda: True
        )
        monkeypatch.setattr(
            "pynisa._internal.db.read.get_connection",
            lambda readonly: get_connection(
                path=db_path_with_data, readonly=readonly
            ),
        )

        df = read_ranking("rakuten", "jp_stock_buy")
        assert df is not None
        assert len(df) == 3
        # Latest date (2026-03-07)
        assert df.iloc[0]["ticker"] == "8306"

    def test_read_ranking_with_date(
        self, db_path_with_data: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "pynisa._internal.db.read.db_exists", lambda: True
        )
        monkeypatch.setattr(
            "pynisa._internal.db.read.get_connection",
            lambda readonly: get_connection(
                path=db_path_with_data, readonly=readonly
            ),
        )

        df = read_ranking(
            "rakuten", "jp_stock_buy", date="2026-02-28"
        )
        assert df is not None
        assert df.iloc[0]["ticker"] == "7974"

    def test_read_ranking_dates(
        self, db_path_with_data: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "pynisa._internal.db.read.db_exists", lambda: True
        )
        monkeypatch.setattr(
            "pynisa._internal.db.read.get_connection",
            lambda readonly: get_connection(
                path=db_path_with_data, readonly=readonly
            ),
        )

        dates = read_ranking_dates("rakuten", "jp_stock_buy")
        assert dates == ["2026-03-07", "2026-02-28"]

    def test_read_history(
        self, db_path_with_data: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "pynisa._internal.db.read.db_exists", lambda: True
        )
        monkeypatch.setattr(
            "pynisa._internal.db.read.get_connection",
            lambda readonly: get_connection(
                path=db_path_with_data, readonly=readonly
            ),
        )

        df = read_history("rakuten", "7974", category="jp_stock_buy")
        assert len(df) == 2
        assert df.iloc[0]["date"] == "2026-03-07"
        assert df.iloc[0]["rank"] == 2
        assert df.iloc[1]["date"] == "2026-02-28"
        assert df.iloc[1]["rank"] == 1

    def test_read_ranking_no_db(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "pynisa._internal.db.read.db_exists", lambda: False
        )
        assert read_ranking("rakuten", "jp_stock_buy") is None
        assert read_ranking_dates("rakuten") == []
        assert read_history("rakuten", "7974").empty

    def test_read_meta(
        self, db_path_with_data: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Write meta first
        conn = get_connection(path=db_path_with_data, readonly=False)
        update_meta(conn, "test_key", "test_value")
        conn.close()

        monkeypatch.setattr(
            "pynisa._internal.db.read.db_exists", lambda: True
        )
        monkeypatch.setattr(
            "pynisa._internal.db.read.get_connection",
            lambda readonly: get_connection(
                path=db_path_with_data, readonly=readonly
            ),
        )

        assert read_meta("test_key") == "test_value"
        assert read_meta("nonexistent") is None
