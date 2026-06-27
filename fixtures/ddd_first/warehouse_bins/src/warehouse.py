class Warehouse:
    """Aggregate root over capacity-bounded bins with conserving transfers."""

    def __init__(self):
        self.caps: dict[str, int] = {}
        self.qty: dict[str, int] = {}
        self.events: list[str] = []

    def add_bin(self, bin_id: str, capacity: int) -> None:
        raise NotImplementedError("implement add_bin per DOMAIN.md")

    def receive(self, bin_id: str, qty: int) -> None:
        raise NotImplementedError("implement receive per DOMAIN.md")

    def transfer(self, src: str, dst: str, qty: int) -> None:
        raise NotImplementedError("implement transfer per DOMAIN.md")

    def quantity(self, bin_id: str) -> int:
        raise NotImplementedError("implement quantity per DOMAIN.md")

    def total_stock(self) -> int:
        raise NotImplementedError("implement total_stock per DOMAIN.md")
