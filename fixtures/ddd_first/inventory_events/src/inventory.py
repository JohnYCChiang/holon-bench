class Inventory:
    """Aggregate root for one SKU. Records domain events; never goes negative."""

    def __init__(self, available: int, reorder_to: int):
        if available < 0:
            raise ValueError("available must be non-negative")
        if reorder_to <= 0:
            raise ValueError("reorder_to must be positive")
        self.available = available
        self.reorder_to = reorder_to
        self.events: list[str] = []
        self._reorder_pending = False

    def reserve(self, qty: int) -> None:
        raise NotImplementedError("implement reserve per DOMAIN.md")

    def apply_reorder_policy(self) -> None:
        raise NotImplementedError("implement apply_reorder_policy per DOMAIN.md")
