#!/usr/bin/env python3
import sys

parts = sys.stdin.read().split("\n")
result = parts[0] if parts else ""
for b in parts[1:]:
    if b.startswith("/"):
        result = b
    elif result == "" or result.endswith("/"):
        result += b
    else:
        result += "/" + b
print(result)
