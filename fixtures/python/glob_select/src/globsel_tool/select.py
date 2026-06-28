from __future__ import annotations


def select_paths(paths, include, exclude):
    selected = []
    for path in paths:
        if any(pattern in path for pattern in include):
            selected.append(path)
    return {"ok": True, "selected": selected, "excluded": []}
