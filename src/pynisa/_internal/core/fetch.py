"""HTTP fetch layer. Does I/O only, returns raw text."""

from __future__ import annotations

import httpx

_TIMEOUT = 30.0
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
}


def fetch_text(url: str, *, encoding: str | None = None) -> str:
    """Fetch URL and return response body as text.

    Parameters
    ----------
    url : str
        URL to fetch.
    encoding : str, optional
        Force response encoding (e.g. "shift_jis"). If None, httpx
        auto-detects from headers.

    Returns
    -------
    str
        Response body as decoded text.

    Raises
    ------
    httpx.HTTPStatusError
        If the response status code indicates an error.
    """
    with httpx.Client(
        headers=_HEADERS, timeout=_TIMEOUT, follow_redirects=True
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        if encoding is not None:
            response.encoding = encoding
        return response.text
