from __future__ import annotations


def compact_output(result: dict, max_chars: int) -> dict:
    output = result.get("output", "")
    if len(output) <= max_chars:
        return dict(result)
    truncated = dict(result)
    truncated["output"] = output[:max_chars]
    return truncated
