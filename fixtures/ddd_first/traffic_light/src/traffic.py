class TrafficLight:
    NEXT = {"GREEN": "YELLOW", "YELLOW": "RED", "RED": "GREEN"}

    def __init__(self, start: str = "GREEN"):
        if start not in self.NEXT:
            raise ValueError("unknown phase")
        self.current = start
        self.events: list = []
        self._walk_pending = False

    def advance(self) -> None:
        raise NotImplementedError("implement advance per DOMAIN.md")

    def request_walk(self) -> None:
        raise NotImplementedError("implement request_walk per DOMAIN.md")
