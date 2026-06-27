# Domain: Library (bounded context)

Implement `src/library.py`. A `Library` lends copies to patrons under a
per-patron loan limit.

## Library (aggregate root)
- Created with a positive integer `max_loans` (per patron) (`ValueError`).
- Tracks copies, per-patron loan counts, and an `events` list (starts empty).
- `add_copy(copy_id)` registers a copy.
  - Invariant: `copy_id` must be non-empty and not already registered
    (`ValueError`). A new copy starts available.
- `borrow(patron, copy_id)`:
  - Invariant: `patron` must be non-empty (`ValueError`).
  - Invariant: `copy_id` must exist and be available (`ValueError`).
  - Invariant: the patron's current loans must be `< max_loans` (`ValueError`).
  - A rejected command must not mutate state.
  - On success: mark the copy as held by the patron, increment the patron's loan
    count, append a `"Borrowed"` event.
- `return_copy(copy_id)`:
  - Invariant: `copy_id` must exist and currently be on loan (`ValueError`).
  - On success: free the copy, decrement the holder's loan count, append a
    `"Returned"` event.
- `is_available(copy_id)` returns whether the copy is free.
- `loans_of(patron)` returns the patron's current loan count.

Only edit `src/library.py`.
