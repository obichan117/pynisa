"""SBI Securities NISA ranking source."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import yaml
from bs4 import BeautifulSoup

from pynisa._internal.core.fetch import fetch_text
from pynisa._internal.sources import _register
from pynisa._internal.sources.base import NisaSource, RankingResult

_CONFIG_PATH = Path(__file__).with_suffix(".yaml")


class SbiSource(NisaSource):
    """Fetches NISA rankings from SBI Securities HTML pages."""

    def __init__(self) -> None:
        with open(_CONFIG_PATH) as f:
            self._config: dict = yaml.safe_load(f)
        self._html_cache: dict[str, str] = {}

    @property
    def name(self) -> str:
        return "sbi"

    @property
    def display_name(self) -> str:
        return self._config["display_name"]

    def categories(self) -> list[str]:
        return list(self._config["categories"])

    def asset_types(self) -> dict[str, str]:
        return dict(self._config.get("asset_types", {}))

    def fetch_ranking(
        self, category: str | None = None, *, count: int = 10
    ) -> RankingResult:
        cat = category or self._config["default_category"]
        if cat not in self._config["categories"]:
            available = ", ".join(self.categories())
            raise ValueError(
                f"Unknown category: {cat!r}. Available: {available}"
            )

        cat_cfg = self._config["categories"][cat]
        url_key = cat_cfg["url_key"]

        if url_key not in self._html_cache:
            url = self._config["urls"][url_key].replace("\n", "").replace(" ", "")
            self._html_cache[url_key] = fetch_text(
                url, encoding=self._config.get("encoding")
            )

        html = self._html_cache[url_key]
        df = _parse_ranking(
            html,
            section_index=cat_cfg["table_index"],
            has_ticker=cat_cfg["has_ticker"],
        )
        period = _extract_period(html)

        # Rename direction → change
        if "direction" in df.columns:
            df = df.rename(columns={"direction": "change"})

        df["source"] = "sbi"
        df["category"] = cat
        return RankingResult(data=df.head(count), period=period)


def _extract_period(html: str) -> str:
    """Extract the ranking period from SBI HTML."""
    # Look for patterns like "2026/3/9 〜 2026/3/13"
    match = re.search(
        r"(20\d{2}/\d{1,2}/\d{1,2}\s*[～〜]\s*20\d{2}/\d{1,2}/\d{1,2})", html
    )
    if match:
        return match.group(1)
    # Try "YYYY/M/D 現在" pattern
    match = re.search(r"(20\d{2}/\d{1,2}/\d{1,2}\s*現在)", html)
    if match:
        return match.group(1)
    return ""


def _parse_ranking(
    html: str,
    *,
    section_index: int,
    has_ticker: bool,
) -> pd.DataFrame:
    """Parse SBI ranking HTML into a DataFrame (no I/O).

    SBI uses a single large table with multiple ranking sections
    separated by header rows starting with '順位'.
    """
    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one("table")
    if table is None:
        return pd.DataFrame(columns=["rank", "direction", "name", "ticker"])

    # Split rows into sections by header rows ("順位").
    # Content before the first header is discarded.
    sections: list[list[list[str]]] = []
    current: list[list[str]] | None = None
    seen_header = False

    for tr in table.select("tr"):
        cells = tr.select("td, th")
        if not cells:
            continue
        texts = [c.get_text(strip=True) for c in cells]
        if texts[0] == "順位":
            if seen_header and current:
                sections.append(current)
            current = []
            seen_header = True
        elif seen_header and current is not None:
            current.append(texts)

    if current:
        sections.append(current)

    if section_index >= len(sections):
        return pd.DataFrame(columns=["rank", "direction", "name", "ticker"])

    section = sections[section_index]
    return _section_to_df(section, has_ticker=has_ticker)


def _section_to_df(
    rows: list[list[str]], *, has_ticker: bool
) -> pd.DataFrame:
    """Convert a section of text rows into a DataFrame."""
    records: list[dict[str, str]] = []
    rank_counter = 0

    for row in rows:
        if len(row) < 3:
            continue

        rank_counter += 1

        if has_ticker:
            rank = row[0] if row[0] else str(rank_counter)
            direction = row[1]
            ticker = row[2]
            name = row[3] if len(row) > 3 else ""
            records.append({
                "rank": rank,
                "direction": direction,
                "ticker": ticker,
                "name": name,
            })
        else:
            rank = row[0]
            direction = row[2] if len(row) > 2 else ""
            name = row[3] if len(row) > 3 else ""
            records.append({
                "rank": rank,
                "direction": direction,
                "ticker": "",
                "name": name,
            })

    df = pd.DataFrame(records)
    if "rank" in df.columns:
        rank_normalized = df["rank"].str.translate(
            str.maketrans("０１２３４５６７８９", "0123456789")
        )
        df["rank"] = pd.to_numeric(rank_normalized, errors="coerce").astype("Int64")
    return df


_register("sbi", SbiSource)
