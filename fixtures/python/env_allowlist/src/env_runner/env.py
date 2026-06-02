from __future__ import annotations

import os


def build_env(request_env: dict | None = None, allowlist: list[str] | None = None) -> dict:
    env = dict(os.environ)
    env.update(request_env or {})
    return {"env": env, "keys": sorted(env)}
