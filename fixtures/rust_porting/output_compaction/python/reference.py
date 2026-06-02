#!/usr/bin/env python3
import sys

limit = int(sys.argv[1])
lines = sys.stdin.read().splitlines()
if len(lines) <= limit:
    print(f"omitted=0;body={'|'.join(lines)}")
else:
    kept = lines[-limit:]
    print(f"omitted={len(lines)-limit};body={'|'.join(kept)}")
