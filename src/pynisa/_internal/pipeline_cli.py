"""CLI entry point for the ranking pipeline (used by GitHub Actions)."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from pynisa._internal.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch all NISA rankings and store in the database."
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="Database file path (default: ~/.cache/pynisa/nisa.db)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Seconds between HTTP requests (default: 0.5)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    run_pipeline(db_path=args.db, delay=args.delay)


if __name__ == "__main__":
    main()
