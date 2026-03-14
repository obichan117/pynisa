"""Tests for SBI source (offline, using fixtures)."""

from __future__ import annotations

from unittest.mock import patch

from pynisa._internal.sources.sbi import SbiSource, _parse_ranking


class TestParseRanking:
    def test_stock_section_0(self, sbi_stock_html: str) -> None:
        df = _parse_ranking(sbi_stock_html, section_index=0, has_ticker=True)
        assert len(df) == 5
        assert df.iloc[0]["ticker"] == "8306"
        assert df.iloc[0]["direction"] == "→"
        assert df.iloc[0]["rank"] == 1

    def test_stock_section_1(self, sbi_stock_html: str) -> None:
        df = _parse_ranking(sbi_stock_html, section_index=1, has_ticker=True)
        assert len(df) == 5
        assert df.iloc[0]["ticker"] == "6740"

    def test_stock_section_2(self, sbi_stock_html: str) -> None:
        df = _parse_ranking(sbi_stock_html, section_index=2, has_ticker=True)
        assert len(df) == 5
        assert df.iloc[0]["ticker"] == "9432"

    def test_fund_section(self, sbi_fund_html: str) -> None:
        df = _parse_ranking(sbi_fund_html, section_index=0, has_ticker=False)
        assert len(df) == 3
        assert df.iloc[0]["name"] == "eMAXIS Slim 全世界株式"
        assert df.iloc[0]["direction"] == "→"

    def test_out_of_range_section(self, sbi_stock_html: str) -> None:
        df = _parse_ranking(sbi_stock_html, section_index=99, has_ticker=True)
        assert df.empty

    def test_empty_html(self) -> None:
        df = _parse_ranking("<html></html>", section_index=0, has_ticker=True)
        assert df.empty


class TestSbiSource:
    def test_categories(self) -> None:
        src = SbiSource()
        cats = src.categories()
        assert "stock_buy" in cats
        assert "fund_buy" in cats
        assert len(cats) == 11

    def test_name(self) -> None:
        src = SbiSource()
        assert src.name == "sbi"

    def test_invalid_category(self) -> None:
        src = SbiSource()
        import pytest

        with pytest.raises(ValueError, match="Unknown category"):
            src.fetch_ranking("nonexistent")

    def test_fetch_with_mock(self, sbi_stock_html: str) -> None:
        src = SbiSource()
        with patch(
            "pynisa._internal.sources.sbi.fetch_text",
            return_value=sbi_stock_html,
        ):
            result = src.fetch_ranking("stock_buy", count=3)
        assert len(result.data) == 3
        assert result.data.iloc[0]["source"] == "sbi"
        assert "change" in result.data.columns
