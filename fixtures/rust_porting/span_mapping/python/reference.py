#!/usr/bin/env python3
import sys

text = sys.argv[1]
offset = int(sys.argv[2])
offset = min(offset, len(text.encode("utf-8")))
line = 1
col = 1
byte_pos = 0
for ch in text:
    if byte_pos >= offset:
        break
    byte_pos += len(ch.encode("utf-8"))
    if ch == "\n":
        line += 1
        col = 1
    else:
        col += 1
print(f"{line}:{col}")
