#!/usr/bin/env python3
import sys

lines = sys.stdin.read().split("\n")
template = lines[0] if lines else ""
variables = {}
for line in lines[1:]:
    if line == "":
        continue
    k, _, v = line.partition("=")
    variables[k.strip()] = v

out = []
i = 0
n = len(template)
done = False
while i < n:
    if template[i:i + 2] == "{{":
        end = template.find("}}", i + 2)
        if end == -1:
            out.append(template[i])
            i += 1
            continue
        name = template[i + 2:end].strip()
        if name not in variables:
            print(f"error=missing:{name}")
            done = True
            break
        out.append(variables[name])
        i = end + 2
    else:
        out.append(template[i])
        i += 1
if not done:
    print("rendered=" + "".join(out))
