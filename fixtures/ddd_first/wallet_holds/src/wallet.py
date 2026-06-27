class Bank:
    """Aggregate root over wallets and two-phase transfer holds."""

    def __init__(self):
        self.balances: dict[str, int] = {}
        self.held: dict[str, int] = {}
        self.holds: dict[int, dict] = {}
        self.events: list[str] = []
        self._next_hold_id = 1

    def open(self, wallet_id: str, initial: int = 0) -> None:
        raise NotImplementedError("implement open per DOMAIN.md")

    def available(self, wallet_id: str) -> int:
        raise NotImplementedError("implement available per DOMAIN.md")

    def place_hold(self, wallet_id: str, amount: int) -> int:
        raise NotImplementedError("implement place_hold per DOMAIN.md")

    def capture(self, hold_id: int, to_wallet_id: str) -> None:
        raise NotImplementedError("implement capture per DOMAIN.md")

    def release(self, hold_id: int) -> None:
        raise NotImplementedError("implement release per DOMAIN.md")

    def total_balance(self) -> int:
        raise NotImplementedError("implement total_balance per DOMAIN.md")
