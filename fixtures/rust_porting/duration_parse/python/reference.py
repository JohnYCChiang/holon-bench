#!/usr/bin/env python3
import sys

s = sys.stdin.read().strip()
mult = {"d": 86400, "h": 3600, "m": 60, "s": 1}
if s == "":
    print("error=invalid")
    sys.exit(0)
pos = 0
total = 0
n = len(s)
valid = True
while pos < n:
    start = pos
    while pos < n and s[pos].isdigit():
        pos += 1
    if pos == start:
        valid = False
        break
    num = int(s[start:pos])
    if pos >= n or s[pos] not in mult:
        valid = False
        break
    total += num * mult[s[pos]]
    pos += 1
if valid:
    print(f"seconds={total}")
else:
    print("error=invalid")
