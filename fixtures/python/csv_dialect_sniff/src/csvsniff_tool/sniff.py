from __future__ import annotations


def sniff(sample):
    lines = sample.splitlines()
    columns = len(lines[0].split(",")) if lines else 0
    return {"ok": True, "delimiter": ",", "has_header": True, "columns": columns}
