#!/usr/bin/env python3
import sys

s = sys.stdin.read()
if s.endswith("\n"):
    s = s[:-1]
tokens = []
cur = ""
have = False
i = 0
n = len(s)
err = False
while i < n:
    c = s[i]
    if c == "\\":
        if i + 1 < n:
            cur += s[i + 1]
            have = True
            i += 2
        else:
            cur += "\\"
            have = True
            i += 1
    elif c == "'":
        j = s.find("'", i + 1)
        if j == -1:
            err = True
            break
        cur += s[i + 1:j]
        have = True
        i = j + 1
    elif c == '"':
        j = s.find('"', i + 1)
        if j == -1:
            err = True
            break
        cur += s[i + 1:j]
        have = True
        i = j + 1
    elif c == " " or c == "\t":
        if have:
            tokens.append(cur)
            cur = ""
            have = False
        i += 1
    else:
        cur += c
        have = True
        i += 1
if err:
    print("error=unbalanced")
else:
    if have:
        tokens.append(cur)
    print("tokens=" + "|".join(tokens))
