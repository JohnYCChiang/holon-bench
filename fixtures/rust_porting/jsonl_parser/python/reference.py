#!/usr/bin/env python3
import json
import sys

records = []
errors = []
for index, line in enumerate(sys.stdin.read().splitlines(), start=1):
    if not line.strip():
        continue
    try:
        records.append(json.loads(line)["id"])
    except Exception:
        errors.append(index)
print(f"records={','.join(map(str, records))};errors={','.join(map(str, errors))}")
