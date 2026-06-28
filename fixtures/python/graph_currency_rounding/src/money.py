from decimal import Decimal, ROUND_HALF_UP


def format_amount(amount, currency):
    """Format a monetary amount (legacy: always two decimal places)."""
    value = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{value}"
