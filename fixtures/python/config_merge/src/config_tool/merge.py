from __future__ import annotations


def merge_layers(layers):
    result = {}
    for layer in layers:
        result.update(layer)
    return {"ok": True, "config": result}
