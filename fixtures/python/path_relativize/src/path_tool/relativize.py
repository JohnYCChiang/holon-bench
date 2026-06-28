def relativize(path, base):
    if not path.startswith("/") or not base.startswith("/"):
        return {"ok": False, "error": {"code": "not_absolute"}}
    if not base.endswith("/"):
        base = base + "/"
    if path.startswith(base):
        return {"ok": True, "rel": path[len(base):]}
    return {"ok": True, "rel": path}
