#!/usr/bin/env python3
import json
import sys

request = json.loads(sys.argv[1])
allow = set(request["allow"])
incoming = request["env"]
out = {"HOME": "/home/tool", "PATH": "/usr/bin"}
for key in sorted(allow):
    if key in ("HOME", "PATH"):
        continue
    if key in incoming:
        out[key] = incoming[key]
print(",".join(sorted(out)))
