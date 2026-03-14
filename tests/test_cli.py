"""Tests for CLI app."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
from typer.testing import CliRunner

from pynisa._internal.cli.app import app
from pynisa._internal.sources.base import RankingResult

runner = CliRunner()


def _mock_result() -> RankingResult:
    df = pd.DataFrame(
        {
            "rank": [1, 2, 3],
            "change": ["↑", "↓", "→"],
            "ticker": ["7974", "9432", "8306"],
            "name": ["任天堂", "NTT", "三菱UFJ"],
            "source": ["rakuten", "rakuten", "rakuten"],
            "category": ["jp_stock_buy"] * 3,
        }
    )
    return RankingResult(data=df, period="2026年2月1日～2026年2月28日")


class TestRankingCommand:
    def test_table_output(self) -> None:
        with patch("pynisa.ranking", return_value=_mock_result()):
            result = runner.invoke(app, ["rakuten"])
        assert result.exit_code == 0
        assert "任天堂" in result.output

    def test_csv_output(self) -> None:
        with patch("pynisa.ranking", return_value=_mock_result()):
            result = runner.invoke(app, ["rakuten", "-f", "csv"])
        assert result.exit_code == 0
        assert "7974" in result.output

    def test_json_output(self) -> None:
        with patch("pynisa.ranking", return_value=_mock_result()):
            result = runner.invoke(app, ["rakuten", "-f", "json"])
        assert result.exit_code == 0
        assert '"ticker"' in result.output

    def test_count_option(self) -> None:
        with patch("pynisa.ranking", return_value=_mock_result()) as mock:
            runner.invoke(app, ["rakuten", "-n", "5"])
            mock.assert_called_once_with(
                "rakuten", None, count=5, date=None, live=False
            )

    def test_period_shown(self) -> None:
        with patch("pynisa.ranking", return_value=_mock_result()):
            result = runner.invoke(app, ["rakuten"])
        assert "2026年2月" in result.output


class TestDefaultCommand:
    def test_no_args_shows_all(self) -> None:
        with patch("pynisa.ranking", return_value=_mock_result()):
            result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "楽天" in result.output
        assert "SBI" in result.output


class TestSourcesCommand:
    def test_list_sources(self) -> None:
        result = runner.invoke(app, ["sources"])
        assert result.exit_code == 0
        assert "rakuten" in result.output
        assert "sbi" in result.output


class TestCategoriesCommand:
    def test_list_categories(self) -> None:
        result = runner.invoke(app, ["categories", "rakuten"])
        assert result.exit_code == 0
        assert "jp_stock_buy" in result.output

    def test_invalid_source(self) -> None:
        result = runner.invoke(app, ["categories", "nonexistent"])
        assert result.exit_code == 1
