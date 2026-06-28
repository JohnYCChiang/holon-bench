#!/usr/bin/env python3
import sys
import base64

data = sys.stdin.buffer.read()
print(base64.b32encode(data).decode("ascii"))
