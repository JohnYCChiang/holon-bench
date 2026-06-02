import json
import sys


def timeout_result(max_attempts: int) -> dict:
    return {"ok": False, "error": {"code": "timeout", "attempts": max_attempts}}


print(json.dumps(timeout_result(int(sys.argv[1])), sort_keys=True))
