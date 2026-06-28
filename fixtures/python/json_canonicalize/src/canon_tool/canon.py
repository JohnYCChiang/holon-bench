import json


def canonicalize(obj):
    text = json.dumps(obj)
    return {"ok": True, "text": text}
