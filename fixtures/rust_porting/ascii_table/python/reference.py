#!/usr/bin/env python3
import sys

rows = [
    [c.strip() for c in line.split("|")]
    for line in sys.stdin.read().split("\n")
    if line.strip() != ""
]
ncol = max(len(r) for r in rows)
rows = [r + [""] * (ncol - len(r)) for r in rows]
widths = [max(len(r[i]) for r in rows) for i in range(ncol)]


def fmt(r):
    return " | ".join(r[i].ljust(widths[i]) for i in range(ncol))


lines = [fmt(rows[0])]
lines.append("-+-".join("-" * widths[i] for i in range(ncol)))
for r in rows[1:]:
    lines.append(fmt(r))
print("\n".join(line.rstrip() for line in lines))
