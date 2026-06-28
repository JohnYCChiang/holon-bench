#!/usr/bin/env python3
import sys

raw = sys.stdin.read().strip()
cleaned = raw.replace(" ", "").replace("-", "")
if cleaned == "" or not cleaned.isdigit():
    print("valid=false;len=0")
else:
    digits = [int(c) for c in cleaned]
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    valid = total % 10 == 0
    print(f"valid={'true' if valid else 'false'};len={len(cleaned)}")
