#!/usr/bin/env python3
import json
import sys


def merge(base, over):
    if isinstance(base, dict) and isinstance(over, dict):
        result = dict(base)
        for k, v in over.items():
            if v is None:
                result.pop(k, None)
            elif k in result:
                result[k] = merge(result[k], v)
            else:
                result[k] = v
        return result
    return over


lines = sys.stdin.read().split("\n")
base = json.loads(lines[0])
over = json.loads(lines[1])
print(json.dumps(merge(base, over), sort_keys=True, separators=(",", ":")))
