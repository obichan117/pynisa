"""Pipeline: fetch all rankings and store in the database."""

from __future__ import annotations

import logging
import re
from datetime import date
from pathlib import Path

from pynisa._internal.db.core import get_connection, init_schema
from pynisa._internal.db.write import insert_rankings, set_updated_at
from pynisa._internal.sources import get_source, list_sources

logger = logging.getLogger(__name__)


def run_pipeline(
    *,
    db_path: Path | None = None,
    delay: float = 0.5,
) -> None:
    """Fetch all rankings from all sources and write to the database.

    Parameters
    ----------
    db_path : Path, optional
        Database file path. Defaults to ``~/.cache/pynisa/nisa.db``.
    delay : float
        Seconds to wait between HTTP requests.
    """
    import time

    conn = get_connection(path=db_path, readonly=False)
    try:
        init_schema(conn)

        for source_name in list_sources():
            src = get_source(source_name)
            categories = src.categories()

            for cat in categories:
                try:
                    logger.info(
                        "Fetching %s/%s", source_name, cat
                    )
                    result = src.fetch_ranking(cat, count=100)
                    ranking_date = _extract_date(result.period)

                    n = insert_rankings(
                        conn, source_name, cat, ranking_date, result.data
                    )
                    logger.info(
                        "  %s/%s [%s]: %d rows inserted",
                        source_name, cat, ranking_date, n,
                    )
                except Exception:
                    logger.exception(
                        "  Failed: %s/%s", source_name, cat
                    )

                if delay > 0:
                    time.sleep(delay)

        set_updated_at(conn)
        logger.info("Pipeline complete.")
    finally:
        conn.close()


def _extract_date(period: str) -> str:
    """Extract a YYYY-MM-DD date string from a period string.

    Handles formats like:
    - "2026年2月1日～2026年2月28日" → "2026-02-28" (end date)
    - "2026/3/9 ～ 2026/3/13" → "2026-03-13" (end date)
    - "2026/3/9 現在" → "2026-03-09"

    Falls back to today's date if parsing fails.
    """
    # Try Japanese year format: 2026年2月28日
    matches = re.findall(r"(\d{4})年(\d{1,2})月(\d{1,2})日", period)
    if matches:
        y, m, d = matches[-1]  # last match = end date
        return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"

    # Try slash format: 2026/3/13
    matches = re.findall(r"(\d{4})/(\d{1,2})/(\d{1,2})", period)
    if matches:
        y, m, d = matches[-1]
        return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"

    # Fallback to today
    return date.today().isoformat()
