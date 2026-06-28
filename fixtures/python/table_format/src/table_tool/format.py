from __future__ import annotations


def format_table(rows, columns):
    lines = [" | ".join(columns)]
    for row in rows:
        lines.append(" | ".join(str(row[col]) for col in columns))
    return {"ok": True, "text": "\n".join(lines), "rows": len(rows), "columns": columns}
