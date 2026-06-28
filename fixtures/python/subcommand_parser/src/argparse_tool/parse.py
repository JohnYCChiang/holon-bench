from __future__ import annotations


def parse(argv, spec):
    command = argv[0]
    options = {}
    i = 1
    while i < len(argv):
        token = argv[i]
        name = token
        options[name] = argv[i + 1]
        i += 2
    return {"ok": True, "command": command, "options": options}
