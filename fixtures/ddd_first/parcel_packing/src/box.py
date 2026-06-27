class ShippingBox:
    """Aggregate root enforcing weight and item-count capacity invariants."""

    def __init__(self, max_weight: int, max_items: int):
        if max_weight <= 0:
            raise ValueError("max_weight must be positive")
        if max_items <= 0:
            raise ValueError("max_items must be positive")
        self.max_weight = max_weight
        self.max_items = max_items
        self.items: list[int] = []

    def pack(self, weight: int) -> None:
        raise NotImplementedError("implement pack per DOMAIN.md")

    def total_weight(self) -> int:
        raise NotImplementedError("implement total_weight per DOMAIN.md")

    def count(self) -> int:
        raise NotImplementedError("implement count per DOMAIN.md")

    def remaining_weight(self) -> int:
        raise NotImplementedError("implement remaining_weight per DOMAIN.md")
