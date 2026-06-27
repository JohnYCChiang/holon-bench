class Warranty:
    """Aggregate root approving bounded claims over a coverage window."""

    def __init__(self, purchase_day: int, term_days: int, max_claims: int):
        if purchase_day < 0:
            raise ValueError("purchase_day must be non-negative")
        if term_days <= 0:
            raise ValueError("term_days must be positive")
        if max_claims <= 0:
            raise ValueError("max_claims must be positive")
        self.purchase_day = purchase_day
        self.term_days = term_days
        self.max_claims = max_claims
        self.claims: list = []
        self.events: list[str] = []

    def file_claim(self, day: int, amount: int) -> None:
        raise NotImplementedError("implement file_claim per DOMAIN.md")

    def claims_used(self) -> int:
        raise NotImplementedError("implement claims_used per DOMAIN.md")

    def is_active(self, day: int) -> bool:
        raise NotImplementedError("implement is_active per DOMAIN.md")

    def total_claimed(self) -> int:
        raise NotImplementedError("implement total_claimed per DOMAIN.md")
