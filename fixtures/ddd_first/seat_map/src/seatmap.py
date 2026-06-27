class SeatMap:
    def __init__(self, rows: int, cols: int):
        if rows <= 0 or cols <= 0:
            raise ValueError("rows and cols must be positive")
        self.rows = rows
        self.cols = cols
        self.assignments: dict = {}
        self.passenger_seat: dict = {}
        self.events: list = []

    def assign(self, passenger: str, seat) -> None:
        raise NotImplementedError("implement assign per DOMAIN.md")

    def release(self, passenger: str) -> None:
        raise NotImplementedError("implement release per DOMAIN.md")

    def assign_group(self, passengers, row: int) -> None:
        raise NotImplementedError("implement assign_group per DOMAIN.md")
