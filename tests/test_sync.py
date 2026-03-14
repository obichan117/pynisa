"""Tests for sync module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from pynisa._internal.sync import SyncError, sync


class TestSync:
    def test_skip_if_fresh(self, tmp_path: Path) -> None:
        db_file = tmp_path / "nisa.db"
        db_file.write_bytes(b"fake-db")

        with patch("pynisa._internal.sync.db_path", return_value=db_file):
            # Should not attempt download (file is fresh)
            sync()

    def test_force_download(self, tmp_path: Path) -> None:
        db_file = tmp_path / "nisa.db"
        db_file.write_bytes(b"old-db")

        with (
            patch("pynisa._internal.sync.db_path", return_value=db_file),
            patch("pynisa._internal.sync.httpx") as mock_httpx,
        ):
            mock_response = mock_httpx.stream.return_value.__enter__.return_value
            mock_response.iter_bytes.return_value = [b"new-db"]

            sync(force=True)

    def test_sync_error_on_failure(self, tmp_path: Path) -> None:
        db_file = tmp_path / "nisa.db"

        import httpx

        with (
            patch("pynisa._internal.sync.db_path", return_value=db_file),
            patch(
                "pynisa._internal.sync.httpx.stream",
                side_effect=httpx.HTTPError("fail"),
            ),
        ):
            with pytest.raises(SyncError):
                sync(force=True)
