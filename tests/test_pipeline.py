"""Tests for the pipeline and date extraction."""

from __future__ import annotations

from pynisa._internal.pipeline import _extract_date


class TestExtractDate:
    def test_japanese_period(self) -> None:
        assert (
            _extract_date("2026年2月1日～2026年2月28日") == "2026-02-28"
        )

    def test_slash_period(self) -> None:
        assert (
            _extract_date("2026/3/9 ～ 2026/3/13") == "2026-03-13"
        )

    def test_current_date(self) -> None:
        assert (
            _extract_date("2026/3/9 現在") == "2026-03-09"
        )

    def test_empty_fallback(self) -> None:
        result = _extract_date("")
        # Should return today's date as fallback
        assert len(result) == 10  # YYYY-MM-DD
        assert "-" in result

    def test_single_japanese_date(self) -> None:
        assert (
            _extract_date("2026年3月2日更新") == "2026-03-02"
        )
