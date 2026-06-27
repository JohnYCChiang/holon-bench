# Domain: Recipes / BOM (bounded context)

Implement `src/recipe.py`: an immutable `Recipe` value object that scales by
servings and a `BatchPlan` aggregate that records scaled batches.

## Recipe (value object)
- Immutable; equality by value.
- Fields: `servings` (positive integer) and `ingredients`, a tuple of
  `(name, quantity)` pairs.
- Validation on construction (`ValueError` otherwise):
  - `servings` is a positive integer.
  - `ingredients` is non-empty.
  - every `quantity` is a positive integer.
  - ingredient names are unique.
- `scale_to(target_servings)` returns a NEW `Recipe` for `target_servings`:
  - Invariant: `target_servings` is a positive integer (`ValueError`).
  - Each scaled quantity is `quantity * target_servings / servings` and MUST be a
    whole number; if any does not divide evenly, raise `ValueError`.
  - The original recipe is unchanged.
- `total_quantity()` returns the sum of all ingredient quantities.

## BatchPlan (aggregate root)
- Created with a base `Recipe`; starts with an empty `batches` list and empty
  `events` list.
- `add_batch(target_servings)` scales the base recipe and records it.
  - A rejected scaling (`ValueError` from `scale_to`) must not mutate state.
  - On success: append the scaled `Recipe` to `batches` and append a
    `"BatchScaled"` event.
- `batch_count()` returns the number of recorded batches.
- `total_quantity()` returns the summed `total_quantity()` over all batches.

Only edit `src/recipe.py`.
