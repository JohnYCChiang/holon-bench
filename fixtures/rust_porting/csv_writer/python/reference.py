#!/usr/bin/env python3
import sys

fields = sys.stdin.read().split("\n")


def quote(f):
    if "," in f or '"' in f:
        return '"' + f.replace('"', '""') + '"'
    return f


print(",".join(quote(f) for f in fields))
