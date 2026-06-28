from __future__ import annotations

import os


def check_member(name, linkname=None, root="extract"):
    if name.startswith(".."):
        return {"ok": True, "safe": False, "reason": "parent_traversal", "target": name}
    return {"ok": True, "safe": True, "reason": None, "target": os.path.join(root, name)}
