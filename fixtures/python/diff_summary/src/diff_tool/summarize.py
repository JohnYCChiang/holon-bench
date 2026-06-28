from __future__ import annotations


def summarize_diff(old_lines, new_lines):
    added = len(set(new_lines) - set(old_lines))
    removed = len(set(old_lines) - set(new_lines))
    unchanged = len(set(old_lines) & set(new_lines))
    return {"ok": True, "added": added, "removed": removed, "unchanged": unchanged, "changed": added > 0 or removed > 0}
