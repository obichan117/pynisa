"""pynisa — Fetch NISA account trading rankings from Japanese brokerages."""

from __future__ import annotations

from pynisa._internal.sources import get_source, list_sources
from pynisa._internal.sources.base import RankingResult

_db_checked = False


def ranking(
    source: str,
    category: str | None = None,
    *,
    count: int = 10,
    date: str | None = None,
    live: bool = False,
) -> RankingResult:
    """Fetch NISA ranking from a brokerage.

    By default, reads from the local database (downloading it on
    first use). Falls back to a live HTTP fetch if the database
    is unavailable or the requested data is not found.

    Parameters
    ----------
    source : str
        Brokerage name (e.g. ``"rakuten"``, ``"sbi"``).
    category : str, optional
        Ranking category. Use :func:`categories` to see available options.
        If None, returns the default category.
    count : int
        Maximum number of results (default 10).
    date : str, optional
        Date string (``YYYY-MM-DD``). If None, returns the latest available.
        Only used when reading from the database.
    live : bool
        If True, skip the database and fetch directly from the web.

    Returns
    -------
    RankingResult
        Contains ``.data`` (DataFrame), ``.period``, and ``.updated``.

    Examples
    --------
    >>> import pynisa
    >>> result = pynisa.ranking("rakuten")
    >>> result.data  # DataFrame
    >>> result = pynisa.ranking("rakuten", date="2026-02-28")
    """
    src = get_source(source)
    resolved_cat = category or src._config.get("default_category", "")

    # Try DB first (unless live mode)
    if not live:
        _ensure_db()
        db_result = _read_from_db(
            source, resolved_cat, date=date, count=count
        )
        if db_result is not None:
            return db_result

    # Live fallback (not available for historical dates)
    if date is not None:
        from pynisa._internal.db.read import read_ranking_dates

        available = read_ranking_dates(source, resolved_cat)
        avail_str = ", ".join(available[:5]) if available else "none"
        raise ValueError(
            f"No data for {source}/{resolved_cat} on {date}. "
            f"Available dates: {avail_str}"
        )

    return src.fetch_ranking(category, count=count)


def categories(source: str) -> list[str]:
    """List available ranking categories for a source."""
    src = get_source(source)
    return src.categories()


def sources() -> list[str]:
    """List available brokerage source names."""
    return list_sources()


def dates(source: str, category: str | None = None) -> list[str]:
    """List available dates in the database for a source.

    Returns dates in descending order (newest first).
    """
    from pynisa._internal.db.read import read_ranking_dates

    return read_ranking_dates(source, category)


def history(
    source: str,
    ticker: str,
    *,
    category: str | None = None,
    limit: int = 52,
) -> RankingResult:
    """Return rank history for a ticker over time.

    Parameters
    ----------
    source : str
        Brokerage name.
    ticker : str
        Ticker/code to look up.
    category : str, optional
        Filter to a specific category.
    limit : int
        Maximum number of data points.

    Returns
    -------
    RankingResult
        Contains ``.data`` with columns: date, rank, change, category, name.
    """
    from pynisa._internal.db.read import read_history

    _ensure_db()
    df = read_history(source, ticker, category=category, limit=limit)
    return RankingResult(data=df)


def sync(*, force: bool = False) -> None:
    """Download or update the ranking database from GitHub.

    Parameters
    ----------
    force : bool
        If True, re-download even if the local file is fresh.
    """
    from pynisa._internal.sync import sync as _sync

    _sync(force=force)


def _ensure_db() -> None:
    """Auto-sync the DB if missing or stale. Runs once per session."""
    global _db_checked
    if _db_checked:
        return
    _db_checked = True

    try:
        from pynisa._internal.sync import sync as _sync

        _sync()
    except Exception:
        pass  # graceful — fall through to live fetch


def _read_from_db(
    source: str,
    category: str,
    *,
    date: str | None,
    count: int,
) -> RankingResult | None:
    """Try to read ranking from the local database."""
    from pynisa._internal.db.read import read_ranking

    df = read_ranking(source, category, date=date, count=count)
    if df is None or df.empty:
        return None

    date_val = df["date"].iloc[0] if "date" in df.columns else ""
    return RankingResult(data=df, period=date_val)


__all__ = [
    "ranking",
    "categories",
    "sources",
    "dates",
    "history",
    "sync",
    "RankingResult",
]
