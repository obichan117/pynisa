"""Tests for Rakuten source (offline, using fixtures)."""

from __future__ import annotations

from unittest.mock import patch

from pynisa._internal.sources.rakuten import RakutenSource, _parse_ranking


class TestParseRanking:
    def test_jp_stock(self, rakuten_jp_stock_csv: str) -> None:
        df, period, updated = _parse_ranking(
            rakuten_jp_stock_csv,
            columns=["rank", "direction", "ticker", "name"],
        )
        assert len(df) == 10
        assert df.iloc[0]["ticker"] == "7974"
        assert df.iloc[0]["name"] == "任天堂"
        assert df.iloc[0]["rank"] == 1

    def test_us_stock(self, rakuten_us_stock_csv: str) -> None:
        df, period, updated = _parse_ranking(
            rakuten_us_stock_csv,
            columns=["rank", "direction", "ticker", "name", "sector"],
        )
        assert len(df) == 10
        assert df.iloc[0]["ticker"] == "MSFT"
        assert "sector" in df.columns

    def test_metadata_extraction(self, rakuten_jp_stock_csv: str) -> None:
        _, period, updated = _parse_ranking(
            rakuten_jp_stock_csv,
            columns=["rank", "direction", "ticker", "name"],
        )
        assert "～" in period or "〜" in period
        assert "更新" in updated


class TestRakutenSource:
    def test_categories(self) -> None:
        src = RakutenSource()
        cats = src.categories()
        assert "jp_stock_buy" in cats
        assert "us_stock_buy" in cats
        assert len(cats) == 12

    def test_name(self) -> None:
        src = RakutenSource()
        assert src.name == "rakuten"

    def test_invalid_category(self) -> None:
        src = RakutenSource()
        import pytest

        with pytest.raises(ValueError, match="Unknown category"):
            src.fetch_ranking("nonexistent")

    def test_fetch_with_mock(self, rakuten_jp_stock_csv: str) -> None:
        src = RakutenSource()
        with patch(
            "pynisa._internal.sources.rakuten.fetch_text",
            return_value=rakuten_jp_stock_csv,
        ):
            result = src.fetch_ranking("jp_stock_buy", count=5)
        assert len(result.data) == 5
        assert "source" in result.data.columns
        assert result.data.iloc[0]["source"] == "rakuten"
        assert "change" in result.data.columns
