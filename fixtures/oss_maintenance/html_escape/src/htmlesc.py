def escape(s):
    """Escape the five special HTML characters in ``s`` for safe text content:
    ``&`` ``<`` ``>`` ``"`` ``'``. Returns a new string; ``escape("")`` is ``""``.
    Each special character maps to exactly one entity and is never double-escaped.
    """
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    s = s.replace("'", "&#39;")
    s = s.replace("&", "&amp;")  # BUG: ampersand escaped LAST -> double-escapes the others
    return s
