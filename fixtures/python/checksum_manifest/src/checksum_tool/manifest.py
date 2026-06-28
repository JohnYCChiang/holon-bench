from __future__ import annotations

import hashlib
import os


def build_manifest(root):
    files = []
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if os.path.isfile(path):
            with open(path, "rb") as handle:
                data = handle.read()
            files.append({"path": path, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)})
    return {"ok": True, "files": files, "count": len(files)}
