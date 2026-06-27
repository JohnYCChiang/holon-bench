class SeatMap:
    """Aggregate root managing expiring seat holds and confirmed bookings."""

    def __init__(self, seat_count: int):
        if not isinstance(seat_count, int) or seat_count <= 0:
            raise ValueError("seat_count must be a positive integer")
        self.seat_count = seat_count
        self.now = 0
        self.holds: dict[int, int] = {}
        self.confirmed: set[int] = set()

    def hold(self, seat: int, ttl: int) -> None:
        raise NotImplementedError("implement hold per DOMAIN.md")

    def tick(self, seconds: int) -> None:
        raise NotImplementedError("implement tick per DOMAIN.md")

    def confirm(self, seat: int) -> None:
        raise NotImplementedError("implement confirm per DOMAIN.md")

    def is_free(self, seat: int) -> bool:
        raise NotImplementedError("implement is_free per DOMAIN.md")

    def available_count(self) -> int:
        raise NotImplementedError("implement available_count per DOMAIN.md")
