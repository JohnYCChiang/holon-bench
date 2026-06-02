#!/usr/bin/env python3
import sys

parts = []
for part in sys.argv[1].replace("\\", "/").split("/"):
    if part in ("", "."):
        continue
    if part == "..":
        print("error=unsafe_path")
        raise SystemExit(0)
    parts.append(part)
print("ok=" + "/".join(parts))
