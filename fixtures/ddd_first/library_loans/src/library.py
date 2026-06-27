class Library:
    """Aggregate root lending copies under a per-patron loan limit."""

    def __init__(self, max_loans: int):
        if max_loans <= 0:
            raise ValueError("max_loans must be positive")
        self.max_loans = max_loans
        self.copies: dict[str, "str | None"] = {}
        self.loan_counts: dict[str, int] = {}
        self.events: list[str] = []

    def add_copy(self, copy_id: str) -> None:
        raise NotImplementedError("implement add_copy per DOMAIN.md")

    def borrow(self, patron: str, copy_id: str) -> None:
        raise NotImplementedError("implement borrow per DOMAIN.md")

    def return_copy(self, copy_id: str) -> None:
        raise NotImplementedError("implement return_copy per DOMAIN.md")

    def is_available(self, copy_id: str) -> bool:
        raise NotImplementedError("implement is_available per DOMAIN.md")

    def loans_of(self, patron: str) -> int:
        raise NotImplementedError("implement loans_of per DOMAIN.md")
