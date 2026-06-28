#!/usr/bin/env python3
import sys


def is_hex(c):
    return c in "0123456789abcdefABCDEF"


def dec(s):
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == "+":
            out.append(" ")
            i += 1
        elif c == "%" and i + 2 < n and is_hex(s[i + 1]) and is_hex(s[i + 2]):
            out.append(chr(int(s[i + 1:i + 3], 16)))
            i += 3
        else:
            out.append(c)
            i += 1
    return "".join(out)


data = sys.stdin.read().rstrip("\n")
pairs = []
for idx, part in enumerate(data.split("&")):
    if part == "":
        continue
    key, _, val = part.partition("=")
    pairs.append((dec(key), dec(val), idx))
pairs.sort(key=lambda t: (t[0], t[2]))
print(";".join(f"{k}={v}" for k, v, _ in pairs))
