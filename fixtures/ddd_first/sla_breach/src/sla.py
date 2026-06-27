class SLAMonitor:
    """Aggregate root latching SLA breaches over consecutive readings."""

    def __init__(self, threshold: int, tolerance: int):
        if not isinstance(threshold, int) or threshold < 0:
            raise ValueError("threshold must be a non-negative integer")
        if not isinstance(tolerance, int) or tolerance <= 0:
            raise ValueError("tolerance must be a positive integer")
        self.threshold = threshold
        self.tolerance = tolerance
        self.consecutive = 0
        self.breached = False
        self.events: list[str] = []

    def record(self, value: int) -> None:
        raise NotImplementedError("implement record per DOMAIN.md")

    def is_breached(self) -> bool:
        raise NotImplementedError("implement is_breached per DOMAIN.md")

    def breach_count(self) -> int:
        raise NotImplementedError("implement breach_count per DOMAIN.md")
