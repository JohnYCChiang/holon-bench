from dataclasses import dataclass


@dataclass(frozen=True)
class Nutrition:
    calories: int
    protein: int
    carbs: int
    fat: int

    def scale(self, qty: int) -> "Nutrition":
        raise NotImplementedError("implement Nutrition.scale per DOMAIN.md")

    def add(self, other: "Nutrition") -> "Nutrition":
        raise NotImplementedError("implement Nutrition.add per DOMAIN.md")


class Recipe:
    def __init__(self):
        self.items: list = []

    def add_ingredient(self, name: str, nutrition: "Nutrition", qty: int) -> None:
        if qty <= 0:
            raise ValueError("qty must be positive")
        self.items.append((name, nutrition, qty))

    def total(self) -> "Nutrition":
        raise NotImplementedError("implement Recipe.total per DOMAIN.md")
