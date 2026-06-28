#!/usr/bin/env python3
import sys
import json

data = {"": {}}
section = ""
for line in sys.stdin.read().split("\n"):
    s = line.strip()
    if not s or s[0] in ";#":
        continue
    if s.startswith("[") and s.endswith("]"):
        section = s[1:-1].strip()
        data.setdefault(section, {})
    elif "=" in s:
        k, v = s.split("=", 1)
        data[section][k.strip()] = v.strip()
if not data[""]:
    del data[""]
print(json.dumps(data, sort_keys=True, separators=(",", ":")))
