import re


def redact(text, patterns):
    count = 0
    result = text
    for pat in patterns:
        new = re.sub(pat, "[REDACTED]", result)
        if new != result:
            count += 1
        result = new
    return {"ok": True, "text": result, "count": count}
