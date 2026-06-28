from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit


def sanitize(url):
    parts = urlsplit(url)
    cleaned = urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))
    return {"ok": True, "url": cleaned, "removed_credentials": False}
