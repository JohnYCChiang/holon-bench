#!/usr/bin/env python3
import sys

out = []
for line in sys.stdin.read().split("\n"):
    if line.strip() == "":
        continue
    if ":" not in line:
        continue
    level, _, msg = line.partition(":")
    out.append(f"{level.strip().upper()} {msg.strip()}")
print("\n".join(out))
