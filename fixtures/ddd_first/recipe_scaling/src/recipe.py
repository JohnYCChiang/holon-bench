from dataclasses import dataclass


@dataclass(frozen=True)
class Recipe:
    """Value object: an ingredient bill scalable by servings."""

    servings: int
    ingredients: tuple

    def scale_to(self, target_servings: int) -> "Recipe":
        raise NotImplementedError("implement scale_to per DOMAIN.md")

    def total_quantity(self) -> int:
        raise NotImplementedError("implement total_quantity per DOMAIN.md")


class BatchPlan:
    """Aggregate root recording scaled production batches."""

    def __init__(self, base: Recipe):
        self.base = base
        self.batches: list = []
        self.events: list[str] = []

    def add_batch(self, target_servings: int) -> None:
        raise NotImplementedError("implement add_batch per DOMAIN.md")

    def batch_count(self) -> int:
        raise NotImplementedError("implement batch_count per DOMAIN.md")

    def total_quantity(self) -> int:
        raise NotImplementedError("implement total_quantity per DOMAIN.md")
