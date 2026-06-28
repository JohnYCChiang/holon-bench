#!/usr/bin/env python3
import sys

out = []
for line in sys.stdin.read().split("\n"):
    line = line.strip()
    if line == "":
        continue
    try:
        code = int(line)
    except ValueError:
        out.append(f"{line}=error")
        continue
    if 200 <= code <= 399:
        d = "ok"
    elif 400 <= code <= 499:
        d = "retry" if code in (408, 429) else "fail"
    elif 500 <= code <= 599:
        d = "fail" if code in (501, 505) else "retry"
    else:
        d = "error"
    out.append(f"{code}={d}")
print(";".join(out))
