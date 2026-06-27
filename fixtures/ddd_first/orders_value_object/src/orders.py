from dataclasses import dataclass, field


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def add(self, other: "Money") -> "Money":
        raise NotImplementedError("implement Money.add per DOMAIN.md")


class Order:
    """Aggregate root. All line items share the order's currency."""

    def __init__(self, currency: str):
        self.currency = currency
        self.items: list[tuple[str, Money, int]] = []

    def add_item(self, name: str, price: Money, quantity: int) -> None:
        raise NotImplementedError("implement Order.add_item per DOMAIN.md")

    def total(self) -> Money:
        raise NotImplementedError("implement Order.total per DOMAIN.md")
