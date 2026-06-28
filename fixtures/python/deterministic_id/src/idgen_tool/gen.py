from __future__ import annotations

import hashlib


def make_id(namespace, fields):
    raw = namespace + str(fields)
    return {"ok": True, "id": hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16], "namespace": namespace}
