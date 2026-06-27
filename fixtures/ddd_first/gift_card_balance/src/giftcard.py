class GiftCard:
    """Aggregate root enforcing a bounded stored-value balance."""

    def __init__(self, max_balance: int):
        if max_balance <= 0:
            raise ValueError("max_balance must be positive")
        self.max_balance = max_balance
        self.balance = 0
        self.events: list[str] = []

    def load(self, amount: int) -> None:
        raise NotImplementedError("implement load per DOMAIN.md")

    def redeem(self, amount: int) -> None:
        raise NotImplementedError("implement redeem per DOMAIN.md")

    def available(self) -> int:
        raise NotImplementedError("implement available per DOMAIN.md")
