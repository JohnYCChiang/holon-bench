#!/usr/bin/env python3
import sys

raw = sys.stdin.read().strip()
neg = raw.startswith("-")
digits = raw.lstrip("+-")
if not digits.isdigit():
    print("error")
else:
    s = digits.lstrip("0") or "0"
    parts = []
    while len(s) > 3:
        parts.append(s[-3:])
        s = s[:-3]
    parts.append(s)
    out = ",".join(reversed(parts))
    print(("-" if neg and out != "0" else "") + out)
