#!/usr/bin/env python3
import sys


def ordinal(n):
    v = abs(n)
    if v % 100 in (11, 12, 13):
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(v % 10, "th")
    return f"{n}{suf}"


toks = sys.stdin.read().split()
print(" ".join(ordinal(int(t)) for t in toks))
