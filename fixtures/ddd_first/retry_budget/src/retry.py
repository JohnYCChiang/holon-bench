class RetryBudget:
    """Authoritative circuit breaker on a monotonic logical clock."""

    def __init__(self, max_failures: int, cooldown: int):
        if max_failures <= 0:
            raise ValueError("max_failures must be positive")
        if cooldown <= 0:
            raise ValueError("cooldown must be positive")
        self.max_failures = max_failures
        self.cooldown = cooldown
        self.state = "CLOSED"
        self.failures = 0
        self.opened_at = None
        self.clock = 0
        self.events: list[str] = []

    def allow(self, now: int) -> bool:
        raise NotImplementedError("implement allow per DOMAIN.md")

    def record_success(self, now: int) -> None:
        raise NotImplementedError("implement record_success per DOMAIN.md")

    def record_failure(self, now: int) -> None:
        raise NotImplementedError("implement record_failure per DOMAIN.md")
