def _parse_version(text):
    parts = text.strip().split(".")
    nums = parts[:3]
    while len(nums) < 3:
        nums.append("0")
    return tuple(nums)


def _cmp(a, b):
    return (a > b) - (a < b)


def _expand(token):
    token = token.strip()
    if token in ("*", "x", ""):
        return [(">=", _parse_version("0.0.0"))]
    if token[0] == "^":
        v = _parse_version(token[1:])
        upper = (str(int(v[0]) + 1), "0", "0")
        return [(">=", v), ("<", upper)]
    if token[0] == "~":
        v = _parse_version(token[1:])
        upper = (v[0], str(int(v[1]) + 1), "0")
        return [(">=", v), ("<", upper)]
    for op in (">=", "<=", ">", "<", "="):
        if token.startswith(op):
            return [(op, _parse_version(token[len(op):]))]
    return [("=", _parse_version(token))]


def _check(version, op, ref):
    c = _cmp(version, ref)
    if op == "=":
        return c == 0
    if op == ">":
        return c > 0
    if op == ">=":
        return c >= 0
    if op == "<":
        return c < 0
    if op == "<=":
        return c <= 0
    return False


def satisfies(version, range_str):
    try:
        v = _parse_version(version)
        for clause in range_str.split("||"):
            tokens = clause.split()
            comparators = []
            for tok in tokens:
                comparators.extend(_expand(tok))
            if not comparators:
                comparators = [(">=", _parse_version("0.0.0"))]
            if all(_check(v, op, ref) for op, ref in comparators):
                return {"ok": True, "match": True}
        return {"ok": True, "match": False}
    except (ValueError, IndexError):
        return {"ok": False, "error": {"code": "invalid_range"}}
