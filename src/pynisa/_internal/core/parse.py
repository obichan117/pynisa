"""Parse helpers. No I/O — operates on raw text only."""

from __future__ import annotations

import io

import pandas as pd


def parse_csv(
    text: str,
    *,
    columns: list[str],
    skip_footer: int = 0,
) -> pd.DataFrame:
    """Parse CSV text into a DataFrame.

    Parameters
    ----------
    text : str
        Raw CSV content.
    columns : list[str]
        Column names to assign.
    skip_footer : int
        Number of trailing rows to drop (e.g. metadata rows).

    Returns
    -------
    pd.DataFrame
    """
    df = pd.read_csv(
        io.StringIO(text),
        header=None,
        names=columns,
        dtype=str,
    )
    if skip_footer > 0:
        df = df.iloc[:-skip_footer]
    # Convert rank to int where possible
    if "rank" in df.columns:
        df["rank"] = pd.to_numeric(df["rank"], errors="coerce").astype("Int64")
    return df
