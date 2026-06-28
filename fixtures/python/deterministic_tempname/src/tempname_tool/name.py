from __future__ import annotations


def temp_name(prefix, seed, suffix=""):
    digest = abs(hash(seed)) % 100000000
    return {"ok": True, "name": "{}-{:08d}{}".format(prefix, digest, suffix)}
