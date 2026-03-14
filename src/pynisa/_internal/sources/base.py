"""Abstract base class for NISA ranking data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd


@dataclass
class RankingResult:
    """Result of a ranking fetch, including data and metadata."""

    data: pd.DataFrame
    period: str = ""
    updated: str = ""


class NisaSource(ABC):
    """Base class for all brokerage NISA ranking sources."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Source identifier (e.g. 'rakuten')."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable source name (e.g. '楽天', 'SBI')."""

    @abstractmethod
    def categories(self) -> list[str]:
        """Return list of available ranking category names."""

    @abstractmethod
    def asset_types(self) -> dict[str, str]:
        """Return mapping of asset type name to default category.

        e.g. {"jp": "jp_stock_buy", "us": "us_stock_buy"}
        """

    @abstractmethod
    def fetch_ranking(
        self, category: str | None = None, *, count: int = 10
    ) -> RankingResult:
        """Fetch ranking data for a given category.

        Returns
        -------
        RankingResult
            Contains DataFrame with columns: rank, change, ticker, name,
            plus metadata (period, updated).
        """
