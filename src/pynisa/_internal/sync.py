"""Download the NISA ranking database from GitHub Releases."""

from __future__ import annotations

import time

import httpx

from pynisa._internal.db.core import db_path

_RELEASE_URL = (
    "https://github.com/obichan117/pynisa/releases/download/db-latest/nisa.db"
)
_FRESHNESS_SECONDS = 24 * 3600  # 1 day


class SyncError(Exception):
    """Raised when database download fails."""


def sync(*, force: bool = False) -> None:
    """Download nisa.db from GitHub Releases.

    Skips download if the local file is fresh (< 1 day old)
    unless ``force=True``.

    Raises
    ------
    SyncError
        If the download fails.
    """
    dest = db_path()

    if not force and dest.is_file():
        age = time.time() - dest.stat().st_mtime
        if age < _FRESHNESS_SECONDS:
            return

    dest.parent.mkdir(parents=True, exist_ok=True)

    try:
        with httpx.stream("GET", _RELEASE_URL, follow_redirects=True) as resp:
            resp.raise_for_status()
            tmp = dest.with_suffix(".tmp")
            with open(tmp, "wb") as f:
                for chunk in resp.iter_bytes(chunk_size=8192):
                    f.write(chunk)
            tmp.rename(dest)  # atomic replace
    except httpx.HTTPError as e:
        raise SyncError(f"Failed to download database: {e}") from e
