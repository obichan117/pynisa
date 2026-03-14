"""Tests for core parse helpers."""

from __future__ import annotations

from pynisa._internal.core.parse import parse_csv


class TestParseCsv:
    def test_basic_csv(self, rakuten_jp_stock_csv: str) -> None:
        df = parse_csv(
            rakuten_jp_stock_csv,
            columns=["rank", "direction", "ticker", "name"],
            skip_footer=2,
        )
        assert len(df) == 10
        assert df.iloc[0]["ticker"] == "7974"
        assert df.iloc[0]["name"] == "任天堂"
        assert df.iloc[0]["rank"] == 1

    def test_csv_with_5_columns(self, rakuten_us_stock_csv: str) -> None:
        df = parse_csv(
            rakuten_us_stock_csv,
            columns=["rank", "direction", "ticker", "name", "sector"],
            skip_footer=2,
        )
        assert len(df) == 10
        assert df.iloc[0]["ticker"] == "MSFT"
        assert df.iloc[0]["sector"] == "ソフトウェア・サービス"

    def test_skip_footer(self, rakuten_jp_stock_csv: str) -> None:
        df_with = parse_csv(
            rakuten_jp_stock_csv,
            columns=["rank", "direction", "ticker", "name"],
            skip_footer=2,
        )
        df_without = parse_csv(
            rakuten_jp_stock_csv,
            columns=["rank", "direction", "ticker", "name"],
            skip_footer=0,
        )
        assert len(df_without) == len(df_with) + 2

    def test_rank_is_int(self, rakuten_jp_stock_csv: str) -> None:
        df = parse_csv(
            rakuten_jp_stock_csv,
            columns=["rank", "direction", "ticker", "name"],
            skip_footer=2,
        )
        assert df["rank"].dtype.name == "Int64"
