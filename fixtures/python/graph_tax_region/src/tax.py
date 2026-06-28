def compute_tax(order):
    """Return tax in minor units for an order (legacy flat rate)."""
    amount = order.get("amount", 0)
    return amount * 1000 // 10000
