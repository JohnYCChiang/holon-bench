from __future__ import annotations


def build_argv(program, args):
    parts = [program] + list(args)
    return {"ok": True, "argv": " ".join(parts), "shell": True}
