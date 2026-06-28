#!/usr/bin/env python3
import sys
import re

raw = sys.stdin.read().strip().lower()
out = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
print(out)
