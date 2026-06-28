from __future__ import annotations


def apply_patch(document, ops):
    doc = document
    for op in ops:
        path = op["path"].split("/")[1:]
        target = doc
        for token in path[:-1]:
            target = target[token]
        key = path[-1]
        if op["op"] in ("add", "replace"):
            target[key] = op["value"]
        elif op["op"] == "remove":
            if key in target:
                del target[key]
    return {"ok": True, "document": doc}
