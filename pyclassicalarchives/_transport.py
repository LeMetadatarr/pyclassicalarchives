"""HTTP transport layer for pyclassicalarchives.

A single shared session is reused across calls. By default it is a
``requests.Session`` with browser-like headers. Set the environment
variable ``PYCLASSICALARCHIVES_TRANSPORT=curl_cffi`` (and install the
``stealth`` extra) to swap in ``curl_cffi`` Chrome TLS impersonation if
classicalarchives.com starts gating plain requests.
"""
from __future__ import annotations

import os
from typing import Any

BASE = "https://www.classicalarchives.com"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json,text/plain,*/*",
}

_session: Any = None


def default_session() -> Any:
    """Return the process-global HTTP session, creating it on first use."""
    global _session
    if _session is None:
        transport = os.environ.get("PYCLASSICALARCHIVES_TRANSPORT", "").strip().lower()
        if transport == "curl_cffi":
            try:
                from curl_cffi import requests as cffi  # type: ignore[import]
                s = cffi.Session(impersonate="chrome")
                s.headers.update(_HEADERS)
                _session = s
                return _session
            except ImportError:
                pass
        import requests
        _session = requests.Session()
        _session.headers.update(_HEADERS)
    return _session


def get_json(path: str, **params: Any) -> Any:
    """GET ``{BASE}{path}`` with query *params* and return parsed JSON.

    Args:
        path:   API path beginning with ``/`` (e.g. ``/api/...``).
        params: Query-string parameters.

    Raises:
        requests.HTTPError: on a non-2xx response.
    """
    s = default_session()
    r = s.get(f"{BASE}{path}", params=params or None, timeout=30)
    r.raise_for_status()
    return r.json()
