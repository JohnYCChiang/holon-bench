class Elevator:
    """Authoritative deterministic LOOK-policy elevator state machine."""

    def __init__(self, floors: int):
        if not isinstance(floors, int) or floors < 2:
            raise ValueError("floors must be an integer >= 2")
        self.floors = floors
        self.current = 1
        self.direction = "IDLE"
        self.requests: set[int] = set()
        self.events: list[str] = []

    def request(self, floor: int) -> None:
        raise NotImplementedError("implement request per DOMAIN.md")

    def step(self) -> None:
        raise NotImplementedError("implement step per DOMAIN.md")

    def run(self) -> list[int]:
        raise NotImplementedError("implement run per DOMAIN.md")

    def pending(self) -> list[int]:
        raise NotImplementedError("implement pending per DOMAIN.md")
