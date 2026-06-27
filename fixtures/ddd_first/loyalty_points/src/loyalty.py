class LoyaltyAccount:
    """Aggregate root accruing/redeeming loyalty points with lifetime tiers."""

    GOLD_THRESHOLD = 1000

    def __init__(self):
        self.balance = 0
        self.lifetime_earned = 0
        self.events: list[str] = []
        self._gold = False

    def earn(self, amount_cents: int) -> None:
        raise NotImplementedError("implement earn per DOMAIN.md")

    def redeem(self, points: int) -> None:
        raise NotImplementedError("implement redeem per DOMAIN.md")

    def tier(self) -> str:
        raise NotImplementedError("implement tier per DOMAIN.md")
