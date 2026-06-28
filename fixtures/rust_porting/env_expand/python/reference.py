#!/usr/bin/env python3
import sys
import re

text = sys.stdin.read()
header, sep, body = text.partition("\n--\n")
env = {}
for line in header.split("\n"):
    if "=" in line:
        k, v = line.split("=", 1)
        env[k] = v


def repl(m):
    if m.group(0) == "$$":
        return "$"
    name = m.group(1) or m.group(2)
    return env.get(name, "")


out = re.sub(r"\$\$|\$\{(\w+)\}|\$(\w+)", repl, body)
sys.stdout.write(out)
