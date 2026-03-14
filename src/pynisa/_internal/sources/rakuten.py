"""Rakuten Securities NISA ranking source."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from pynisa._internal.core.fetch import fetch_text
from pynisa._internal.core.parse import parse_csv
from pynisa._internal.sources import _register
from pynisa._internal.sources.base import NisaSource, RankingResult

_CONFIG_PATH = Path(__file__).with_suffix(".yaml")


class RakutenSource(NisaSource):
    """Fetches NISA rankings from Rakuten Securities CSV endpoints."""

    def __init__(self) -> None:
        with open(_CONFIG_PATH) as f:
            self._config: dict = yaml.safe_load(f)

    @property
    def name(self) -> str:
        return "rakuten"

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
        url = self._config["base_url"] + cat_cfg["file"]

        raw = fetch_text(url)
        df, period, updated = _parse_ranking(
            raw, columns=cat_cfg["columns"]
        )

        # Rename direction → change
        if "direction" in df.columns:
            df = df.rename(columns={"direction": "change"})

        df["source"] = "rakuten"
        df["category"] = cat
        return RankingResult(data=df.head(count), period=period, updated=updated)


def _parse_ranking(
    raw: str, *, columns: list[str]
) -> tuple[pd.DataFrame, str, str]:
    """Parse Rakuten CSV ranking data (no I/O).

    Returns (DataFrame, period_string, updated_string).
    """
    lines = raw.strip().split("\n")

    # Extract metadata from last 2 lines
    period = ""
    updated = ""
    if len(lines) >= 2:
        meta_lines = [line.split(",")[0].strip() for line in lines[-2:]]
        for line in meta_lines:
            if "～" in line or "〜" in line:
                period = line
            elif "更新" in line:
                updated = line

    df = parse_csv(raw, columns=columns, skip_footer=2)
    return df, period, updated


_register("rakuten", RakutenSource)
