def parse_csv(text):
    """Parse ``text`` into a list of rows, each a list of string fields.

    Fields are separated by commas and rows by ``"\\n"``. A field may be wrapped
    in double quotes, in which case embedded commas and newlines are literal and
    a doubled quote ``""`` denotes a single literal quote. An empty string parses
    to ``[]`` (no rows); a trailing newline does not add an empty row.
    """
    # BUG: naive split treats every comma and newline as a separator, so commas
    # and newlines inside a quoted field wrongly break the field apart and the
    # surrounding quote characters are never stripped.
    rows = []
    for line in text.split("\n"):
        rows.append(line.split(","))
    return rows
