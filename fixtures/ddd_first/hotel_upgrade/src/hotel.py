RATES = {"STANDARD": 100, "DELUXE": 160, "SUITE": 250}
RANK = {"STANDARD": 1, "DELUXE": 2, "SUITE": 3}


class Reservation:
    def __init__(self, room_class: str, nights: int, available=None):
        if room_class not in RANK:
            raise ValueError("unknown room class")
        if nights <= 0:
            raise ValueError("nights must be positive")
        self.room_class = room_class
        self.nights = nights
        self.available = set(available) if available is not None else set(RANK)
        self.events: list = []

    def upgrade(self, target: str) -> int:
        raise NotImplementedError("implement upgrade per DOMAIN.md")
