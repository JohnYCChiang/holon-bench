#!/usr/bin/env python3
import sys

raw = sys.stdin.read().strip().lstrip("#").lower()
hexd = set("0123456789abcdef")
if len(raw) == 3 and all(c in hexd for c in raw):
    raw = "".join(c * 2 for c in raw)
if len(raw) == 6 and all(c in hexd for c in raw):
    r = int(raw[0:2], 16)
    g = int(raw[2:4], 16)
    b = int(raw[4:6], 16)
    print(f"{r},{g},{b}")
else:
    print("error")
