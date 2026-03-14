"""Tests for new CLI commands (sync, dates, history, --last, --date)."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
from typer.testing import CliRunner

from pynisa._internal.cli.app import app
from pynisa._internal.sources.base import RankingResult

runner = CliRunner()


def _mock_result(date: str = "2026-03-07") -> RankingResult:
    df = pd.DataFrame({
        "rank": [1, 2, 3],
        "change": ["↑", "↓", "→"],
        "ticker": ["7974", "9432", "8306"],
        "name": ["任天堂", "NTT", "三菱UFJ"],
        "source": ["rakuten"] * 3,
        "category": ["jp_stock_buy"] * 3,
        "date": [date] * 3,
    })
    return RankingResult(data=df, period=date)


class TestDateFlag:
    def test_date_option(self) -> None:
        with patch(
            "pynisa.ranking", return_value=_mock_result()
        ) as mock:
            result = runner.invoke(app, ["rakuten", "--date", "2026-03-07"])
        assert result.exit_code == 0
        mock.assert_called_once_with(
            "rakuten", None, count=10, date="2026-03-07", live=False
        )


class TestLiveFlag:
    def test_live_option(self) -> None:
        with patch(
            "pynisa.ranking", return_value=_mock_result()
        ) as mock:
            result = runner.invoke(app, ["rakuten", "--live"])
        assert result.exit_code == 0
        mock.assert_called_once_with(
            "rakuten", None, count=10, date=None, live=True
        )


class TestLastFlag:
    def test_last_option(self) -> None:
        with (
            patch("pynisa.dates", return_value=["2026-03-07", "2026-02-28"]),
            patch("pynisa.ranking", return_value=_mock_result()),
            patch(
                "pynisa._internal.sources.get_source"
            ) as mock_src,
        ):
            mock_src.return_value._config = {
                "default_category": "jp_stock_buy"
            }
            result = runner.invoke(app, ["rakuten", "--last", "2"])
        assert result.exit_code == 0


class TestSyncCommand:
    def test_sync(self) -> None:
        with (
            patch("pynisa.sync"),
            patch(
                "pynisa._internal.db.read.read_meta",
                return_value="2026-03-07T01:00:00",
            ),
        ):
            result = runner.invoke(app, ["sync"])
        assert result.exit_code == 0
        assert "synced" in result.output.lower()

    def test_sync_force(self) -> None:
        with (
            patch("pynisa.sync") as mock_sync,
            patch(
                "pynisa._internal.db.read.read_meta",
                return_value="2026-03-07",
            ),
        ):
            result = runner.invoke(app, ["sync", "--force"])
        assert result.exit_code == 0
        mock_sync.assert_called_once_with(force=True)


class TestDatesCommand:
    def test_dates(self) -> None:
        with patch(
            "pynisa.dates",
            return_value=["2026-03-07", "2026-02-28"],
        ):
            result = runner.invoke(app, ["dates", "rakuten"])
        assert result.exit_code == 0
        assert "2026-03-07" in result.output

    def test_dates_empty(self) -> None:
        with patch("pynisa.dates", return_value=[]):
            result = runner.invoke(app, ["dates", "rakuten"])
        assert result.exit_code == 0
        assert "sync" in result.output.lower()


class TestHistoryCommand:
    def test_history(self) -> None:
        history_df = pd.DataFrame({
            "date": ["2026-03-07", "2026-02-28"],
            "rank": [2, 1],
            "change": ["↓", "↑"],
            "category": ["jp_stock_buy", "jp_stock_buy"],
            "name": ["任天堂", "任天堂"],
        })
        mock_result = RankingResult(data=history_df)

        with (
            patch("pynisa.history", return_value=mock_result),
            patch("pynisa._db_checked", True),
        ):
            result = runner.invoke(
                app, ["history", "rakuten", "7974"]
            )
        assert result.exit_code == 0
        assert "7974" in result.output
        assert "任天堂" in result.output

    def test_history_empty(self) -> None:
        empty_result = RankingResult(
            data=pd.DataFrame(
                columns=["date", "rank", "change", "category", "name"]
            )
        )
        with patch("pynisa.history", return_value=empty_result):
            result = runner.invoke(
                app, ["history", "rakuten", "9999"]
            )
        assert result.exit_code == 0
        assert "no history" in result.output.lower()
