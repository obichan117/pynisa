"""Tests for public API."""

from __future__ import annotations

import pynisa
from pynisa._internal.sources.base import RankingResult


class TestPublicApi:
    def test_sources(self) -> None:
        srcs = pynisa.sources()
        assert isinstance(srcs, list)
        assert "rakuten" in srcs
        assert "sbi" in srcs

    def test_categories(self) -> None:
        cats = pynisa.categories("rakuten")
        assert isinstance(cats, list)
        assert "jp_stock_buy" in cats

    def test_categories_sbi(self) -> None:
        cats = pynisa.categories("sbi")
        assert "stock_buy" in cats
        assert "fund_buy" in cats

    def test_invalid_source_raises(self) -> None:
        import pytest

        with pytest.raises(ValueError):
            pynisa.ranking("nonexistent")

    def test_invalid_source_categories(self) -> None:
        import pytest

        with pytest.raises(ValueError):
            pynisa.categories("nonexistent")

    def test_ranking_result_type(self) -> None:
        from unittest.mock import patch

        import pandas as pd

        mock_result = RankingResult(
            data=pd.DataFrame({"rank": [1], "name": ["test"]}),
            period="2026年2月",
        )
        with patch("pynisa._internal.sources.get_source") as mock_get:
            mock_get.return_value.fetch_ranking.return_value = mock_result
            result = pynisa.ranking("rakuten")
        assert isinstance(result, RankingResult)
        assert hasattr(result, "data")
        assert hasattr(result, "period")
