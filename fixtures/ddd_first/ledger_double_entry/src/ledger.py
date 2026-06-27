class Ledger:
    """Aggregate root enforcing the double-entry balance invariant."""

    def __init__(self):
        self.balances: dict[str, int] = {}

    def post(self, legs) -> None:
        raise NotImplementedError("implement Ledger.post per DOMAIN.md")

    def balance(self, account: str) -> int:
        raise NotImplementedError("implement Ledger.balance per DOMAIN.md")

    def is_balanced(self) -> bool:
        raise NotImplementedError("implement Ledger.is_balanced per DOMAIN.md")
