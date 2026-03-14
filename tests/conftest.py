"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def rakuten_jp_stock_csv() -> str:
    return (FIXTURES_DIR / "rakuten_jp_stock.csv").read_text()


@pytest.fixture
def rakuten_us_stock_csv() -> str:
    return (FIXTURES_DIR / "rakuten_us_stock.csv").read_text()


@pytest.fixture
def sbi_stock_html() -> str:
    return (FIXTURES_DIR / "sbi_stock.html").read_text(encoding="utf-8")


@pytest.fixture
def sbi_fund_html() -> str:
    return (FIXTURES_DIR / "sbi_fund.html").read_text(encoding="utf-8")
