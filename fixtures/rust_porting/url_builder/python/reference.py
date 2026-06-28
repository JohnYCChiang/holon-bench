#!/usr/bin/env python3
import sys
from urllib.parse import quote

lines = sys.stdin.read().split("\n")
base = lines[0]
params = []
for line in lines[1:]:
    if "=" in line:
        k, v = line.split("=", 1)
        params.append((k, v))
params.sort(key=lambda kv: kv[0])


def enc(s):
    return quote(s, safe="")


qs = "&".join(f"{enc(k)}={enc(v)}" for k, v in params)
print(base + ("?" + qs if qs else ""))
