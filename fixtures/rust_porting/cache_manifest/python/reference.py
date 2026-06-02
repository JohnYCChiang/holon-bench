#!/usr/bin/env python3
import json
import sys

entries = json.loads(sys.argv[1])
entries = sorted(entries, key=lambda item: item["path"])
paths = ",".join(item["path"] for item in entries)
total = sum(item["bytes"] for item in entries)
stale = sum(1 for item in entries if item.get("stale"))
print(f"paths={paths};bytes={total};stale={stale}")
