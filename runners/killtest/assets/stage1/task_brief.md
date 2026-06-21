# Task brief — bounded relational mini-store

This is the project specification for the deliverable and the source of truth for
the required behaviour.

You are extending a small, verified relational mini-store. The library already
provides ~45 pure, total, monomorphic operations over four record shapes, grouped
into bounded contexts (modules):

- `Order{item: Int, qty: Int}`   `Item{id: Int, cat: Int, value: Int}`
- `Line{cat: Int, value: Int}`   `Summary{cat: Int, total: Int}`
- modules: `row` (constructors/predicates), `table` (sort/merge/insert),
  `query` (joins/projections), `agg` (folds/groups), `valid` (invariant checks).

CAP = 64 (the per-category total bound).

## Target edit — author `report`

```
report : &[Order] -> &[Item] -> cap:Int -> Vec<Summary>
```

`report` is the per-category **cap-bounded SUM of `item.value`** over **valid**
orders (`qty > 0`) **inner-joined** to items on `order.item == item.id`:

- a `(order, item)` match contributes `item.value` (quantity is NOT multiplied in);
- group the matched lines by `cat`; sum each group's values with the bounded add
  (saturating, then clamped into `[0, cap]`);
- the result is **sorted-unique by `cat` ascending**, every `total` in `[0, cap]`;
- a `cat` appears iff ≥1 valid matched line carries it; unmatched or invalid
  orders contribute nothing.

You compose `report` from the existing library dependencies — you do not re-author
them. A correct composition exists using only the dependencies' contracts.

## Acceptance + downstream consumer

A visible acceptance suite checks `report` on worked examples. A held-out regression
suite runs at scoring time (never shown to you). `report` must also satisfy
the existing verified consumer `dashboard = merge_summaries(report(...), prev, cap)`,
whose own laws hold only if `report` is correct — so `report` must be a durable,
verified, composable node, not a throwaway.
