def dedup(records):
    seen = set()
    unique = []
    removed = 0
    for rec in records:
        key = rec["id"]
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        unique.append(rec)
    return {"ok": True, "unique": unique, "removed": removed}
