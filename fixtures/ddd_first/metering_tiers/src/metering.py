from dataclasses import dataclass


@dataclass(frozen=True)
class TieredPlan:
    """Value object pricing usage across ascending tiers."""

    tiers: tuple

    def cost(self, units: int) -> int:
        raise NotImplementedError("implement TieredPlan.cost per DOMAIN.md")


class MeteredSubscription:
    """Aggregate root accumulating usage and billing cycles as invoices."""

    def __init__(self, plan: TieredPlan):
        self.plan = plan
        self.usage = 0
        self.invoices: list[int] = []
        self.events: list[str] = []

    def record(self, units: int) -> None:
        raise NotImplementedError("implement record per DOMAIN.md")

    def current_charge(self) -> int:
        raise NotImplementedError("implement current_charge per DOMAIN.md")

    def close_cycle(self) -> int:
        raise NotImplementedError("implement close_cycle per DOMAIN.md")

    def total_billed(self) -> int:
        raise NotImplementedError("implement total_billed per DOMAIN.md")
