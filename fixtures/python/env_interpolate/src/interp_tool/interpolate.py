from __future__ import annotations


def interpolate(template, variables):
    result = template
    for key, value in variables.items():
        result = result.replace("${" + key + "}", str(value))
    return {"ok": True, "result": result, "resolved": list(variables.keys())}
