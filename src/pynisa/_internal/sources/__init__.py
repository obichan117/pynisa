"""Source registry for NISA ranking data providers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pynisa._internal.sources.base import NisaSource

_SOURCES: dict[str, type[NisaSource]] = {}


def _register(name: str, cls: type[NisaSource]) -> None:
    _SOURCES[name] = cls


def get_source(name: str) -> NisaSource:
    """Get an instantiated source by name."""
    if name not in _SOURCES:
        available = ", ".join(sorted(_SOURCES))
        raise ValueError(f"Unknown source: {name!r}. Available: {available}")
    return _SOURCES[name]()


def list_sources() -> list[str]:
    """Return sorted list of available source names."""
    return sorted(_SOURCES)


def get_display_name(name: str) -> str:
    """Return human-readable display name for a source."""
    if name not in _SOURCES:
        return name
    return _SOURCES[name]().display_name


def sources_for_asset(asset_type: str) -> list[tuple[str, str]]:
    """Return list of (source_name, category) that support a given asset type."""
    results = []
    for name in sorted(_SOURCES):
        src = _SOURCES[name]()
        mapping = src.asset_types()
        if asset_type in mapping:
            results.append((name, mapping[asset_type]))
    return results


def _auto_register() -> None:
    """Import all source modules to trigger registration."""
    from pynisa._internal.sources import rakuten as _rakuten  # noqa: F401
    from pynisa._internal.sources import sbi as _sbi  # noqa: F401


_auto_register()
