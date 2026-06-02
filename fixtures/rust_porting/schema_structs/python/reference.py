import json
import sys


def run(payload: dict) -> dict:
    if set(payload) - {"root", "include_hidden"} or "root" not in payload:
        return {"ok": False, "error": {"code": "invalid_request"}}
    return {
        "ok": True,
        "root": payload["root"],
        "include_hidden": payload.get("include_hidden", False),
    }


print(json.dumps(run(json.loads(sys.argv[1])), sort_keys=True))
