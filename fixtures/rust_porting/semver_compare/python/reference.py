#!/usr/bin/env python3
import re
import sys

CORE = re.compile(
    r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$"
)


def parse(v):
    m = CORE.fullmatch(v)
    if not m:
        return None
    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
    pre = m.group(4)
    pre_ids = pre.split(".") if pre is not None else []
    for ident in pre_ids:
        if ident == "":
            return None
        if ident.isdigit() and len(ident) > 1 and ident[0] == "0":
            return None
    return (major, minor, patch, pre_ids)


def cmp_pre(a, b):
    if not a and not b:
        return 0
    if not a:
        return 1
    if not b:
        return -1
    for x, y in zip(a, b):
        xd, yd = x.isdigit(), y.isdigit()
        if xd and yd:
            c = (int(x) > int(y)) - (int(x) < int(y))
        elif xd and not yd:
            c = -1
        elif not xd and yd:
            c = 1
        else:
            c = (x > y) - (x < y)
        if c != 0:
            return c
    return (len(a) > len(b)) - (len(a) < len(b))


def compare(va, vb):
    pa, pb = parse(va), parse(vb)
    if pa is None or pb is None:
        return None
    for i in range(3):
        if pa[i] != pb[i]:
            return -1 if pa[i] < pb[i] else 1
    return cmp_pre(pa[3], pb[3])


lines = sys.stdin.read().split("\n")
a = lines[0] if len(lines) > 0 else ""
b = lines[1] if len(lines) > 1 else ""
r = compare(a, b)
if r is None:
    print("error=invalid")
else:
    print(f"cmp={r}")
