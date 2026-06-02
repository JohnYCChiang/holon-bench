#!/usr/bin/env python3
import sys

errors = []
warnings = 0
for line in sys.stdin.read().splitlines():
    if line.startswith("ERROR:"):
        errors.append(line.removeprefix("ERROR:").strip())
    elif line.startswith("WARN:"):
        warnings += 1
first = errors[0] if errors else ""
print(f"errors={len(errors)};warnings={warnings};first={first}")
