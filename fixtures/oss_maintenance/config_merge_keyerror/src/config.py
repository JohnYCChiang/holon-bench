def merge_config(base, override):
    """Merge ``override`` onto ``base`` and return a new dict.

    ``base`` and ``override`` are plain mappings. The ``limits`` section is
    optional and may be absent from either mapping. ``effective_timeout`` is
    derived from both sides' ``limits.timeout`` (a missing side contributes 0).
    Neither input must be mutated.
    """
    result = dict(base)
    for key in override:
        result[key] = override[key]
    result["effective_timeout"] = base["limits"]["timeout"] + override["limits"]["timeout"]
    return result
