class BankAccount:
    """Aggregate root enforcing balance and daily-limit invariants."""

    def __init__(self, daily_limit: int):
        if daily_limit <= 0:
            raise ValueError("daily_limit must be positive")
        self.daily_limit = daily_limit
        self.balance = 0
        self.withdrawn_today = 0

    def deposit(self, amount: int) -> None:
        raise NotImplementedError("implement deposit per DOMAIN.md")

    def withdraw(self, amount: int) -> None:
        raise NotImplementedError("implement withdraw per DOMAIN.md")
