#!/usr/bin/env python3
import sys
import json

lines = sys.stdin.read().split("\n")
doc = json.loads(lines[0])
pointer = lines[1] if len(lines) > 1 else ""


def resolve(doc, pointer):
    if pointer == "":
        return doc
    if not pointer.startswith("/"):
        return {"error": "not_found"}
    cur = doc
    for tok in pointer.split("/")[1:]:
        tok = tok.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, dict):
            if tok in cur:
                cur = cur[tok]
            else:
                return {"error": "not_found"}
        elif isinstance(cur, list):
            if tok.isdigit() and int(tok) < len(cur):
                cur = cur[int(tok)]
            else:
                return {"error": "not_found"}
        else:
            return {"error": "not_found"}
    return cur


print(json.dumps(resolve(doc, pointer), sort_keys=True, separators=(",", ":")))
