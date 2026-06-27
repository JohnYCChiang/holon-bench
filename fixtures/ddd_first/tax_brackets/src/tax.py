from dataclasses import dataclass


@dataclass(frozen=True)
class TaxSchedule:
    """Value object: a progressive bracket schedule."""

    brackets: tuple

    def tax_for(self, income: int) -> int:
        raise NotImplementedError("implement tax_for per DOMAIN.md")


class TaxReturn:
    """Aggregate root accumulating income and filing once."""

    def __init__(self, schedule: TaxSchedule):
        self.schedule = schedule
        self.income = 0
        self.filed = False
        self.events: list[str] = []

    def add_income(self, amount: int) -> None:
        raise NotImplementedError("implement add_income per DOMAIN.md")

    def file(self) -> int:
        raise NotImplementedError("implement file per DOMAIN.md")

    def current_liability(self) -> int:
        raise NotImplementedError("implement current_liability per DOMAIN.md")
