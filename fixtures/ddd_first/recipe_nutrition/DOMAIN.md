# Domain: Recipe Nutrition (bounded context)

Implement `src/nutrition.py` to satisfy these rules.

## Nutrition (value object)
- Immutable; equality by value. Fields `calories, protein, carbs, fat` are integers
  (per single unit of an ingredient).
- `scale(qty)` returns a new `Nutrition` with every field multiplied by `qty`.
- `add(other)` returns a new `Nutrition` summing each field.

## Recipe (aggregate root)
- Starts empty.
- `add_ingredient(name, nutrition, qty)` appends an ingredient. `qty` must be a
  positive integer (`ValueError` otherwise).
- `total()` returns a `Nutrition` summing each ingredient's `nutrition.scale(qty)`.
  An empty recipe totals `Nutrition(0, 0, 0, 0)`.

Only edit `src/nutrition.py`.
