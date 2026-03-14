"""pynisa — Fetch NISA account trading rankings from Japanese brokerages."""

from __future__ import annotations

from pynisa._internal.sources import get_source, list_sources
from pynisa._internal.sources.base import RankingResult


def ranking(
    source: str,
    category: str | None = None,
    *,
    count: int = 10,
) -> RankingResult:
    """Fetch NISA ranking from a brokerage.

    Parameters
    ----------
    source : str
        Brokerage name (e.g. ``"rakuten"``, ``"sbi"``).
    category : str, optional
        Ranking category. Use :func:`categories` to see available options.
        If None, returns the default category.
    count : int
        Maximum number of results (default 10).

    Returns
    -------
    RankingResult
        Contains ``.data`` (DataFrame), ``.period``, and ``.updated``.

    Examples
    --------
    >>> import pynisa
    >>> result = pynisa.ranking("rakuten")
    >>> result.data  # DataFrame
    >>> result.period  # e.g. "2026年2月1日～2026年2月28日"
    """
    src = get_source(source)
    return src.fetch_ranking(category, count=count)


def categories(source: str) -> list[str]:
    """List available ranking categories for a source."""
    src = get_source(source)
    return src.categories()


def sources() -> list[str]:
    """List available brokerage source names."""
    return list_sources()


__all__ = ["ranking", "categories", "sources", "RankingResult"]
