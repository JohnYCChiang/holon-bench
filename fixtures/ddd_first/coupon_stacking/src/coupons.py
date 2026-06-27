from dataclasses import dataclass


@dataclass(frozen=True)
class Coupon:
    """Value object describing a discount."""

    code: str
    kind: str
    value: int
    stackable: bool


class Checkout:
    """Aggregate root applying coupons under stacking rules."""

    def __init__(self, subtotal: int):
        if not isinstance(subtotal, int) or subtotal <= 0:
            raise ValueError("subtotal must be a positive integer")
        self.subtotal = subtotal
        self.coupons: list[Coupon] = []

    def apply(self, coupon: Coupon) -> None:
        raise NotImplementedError("implement apply per DOMAIN.md")

    def total(self) -> int:
        raise NotImplementedError("implement total per DOMAIN.md")

    def discount(self) -> int:
        raise NotImplementedError("implement discount per DOMAIN.md")
