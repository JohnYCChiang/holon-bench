class ParkingLot:
    """Aggregate root allocating bounded small/large parking slots."""

    def __init__(self, small_slots: int, large_slots: int):
        if small_slots <= 0 or large_slots <= 0:
            raise ValueError("slot counts must be positive")
        self.small_free = small_slots
        self.large_free = large_slots
        self.assignments: dict[str, str] = {}
        self.events: list[str] = []

    def park(self, plate: str, size: str) -> None:
        raise NotImplementedError("implement park per DOMAIN.md")

    def leave(self, plate: str) -> None:
        raise NotImplementedError("implement leave per DOMAIN.md")

    def available_small(self) -> int:
        raise NotImplementedError("implement available_small per DOMAIN.md")

    def available_large(self) -> int:
        raise NotImplementedError("implement available_large per DOMAIN.md")

    def occupancy(self) -> int:
        raise NotImplementedError("implement occupancy per DOMAIN.md")
