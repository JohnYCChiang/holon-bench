def add_numbers(a, b):
    """Add two numbers and return their sum as a float.

    This function currently has a bug: it raises TypeError for float inputs.
    Your task is to fix it.
    """
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Only integers are supported")  # BUG: should accept floats
    return float(a + b)
