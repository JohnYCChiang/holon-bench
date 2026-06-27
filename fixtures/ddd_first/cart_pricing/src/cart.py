from dataclasses import dataclass


@dataclass(frozen=True)
class Discount:
    percent: int

    def apply_to(self, amount: int) -> int:
        raise NotImplementedError("implement Discount.apply_to per DOMAIN.md")


class Cart:
    """Aggregate root. Carries at most one discount; amounts in minor units."""

    def __init__(self, currency: str):
        self.currency = currency
        self.items: list[tuple[str, int, int]] = []
        self.discount = None

    def add_item(self, sku: str, unit_price: int, quantity: int) -> None:
        raise NotImplementedError("implement Cart.add_item per DOMAIN.md")

    def apply_discount(self, discount: "Discount") -> None:
        raise NotImplementedError("implement Cart.apply_discount per DOMAIN.md")

    def subtotal(self) -> int:
        raise NotImplementedError("implement Cart.subtotal per DOMAIN.md")

    def total(self) -> int:
        raise NotImplementedError("implement Cart.total per DOMAIN.md")
