from __future__ import annotations


def encode_cursor(offset, key):
    return "{}:{}".format(offset, key)


def decode_cursor(token):
    offset_str, key = token.split(":", 1)
    return {"ok": True, "offset": int(offset_str), "key": key}
