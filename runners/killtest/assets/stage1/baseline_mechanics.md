# Rust — mechanics

You work in a normal git Rust repo with an Aider-grade repo map.

Substrate: the relational mini-store crate lives in your run dir. The acceptance
suite (`acceptance/rust/tests.rs`) is included as `#[cfg(test)] mod tests;` next to
your implementation. A held-out regression suite runs at scoring time (never shown
to you). You add `pub fn report(...)` composing the existing module functions.

## What you get for free: a machine-checked signature index

The compiler gives you every dependency's **type signature** for free (this index is
`cargo check`-derived, so it is trustworthy and costs you no body reads):

```
row::mk_summary(cat: i64, total: i64) -> Summary
row::bounded_add(a: i64, b: i64, cap: i64) -> i64
table::filter_valid_orders(os: &[Order]) -> Vec<Order>
table::sort_orders(os: &mut Vec<Order>)         table::sort_items(is: &mut Vec<Item>)
table::sorted_unique_insert(xs: &[Summary], x: Summary, cap: i64) -> Vec<Summary>
query::merge_join(orders: &[Order], items: &[Item]) -> Vec<Line>
agg::group_values(ls: &[Line]) -> Vec<(i64, Vec<i64>)>
agg::agg_sum_bounded(xs: &[i64], cap: i64) -> i64
```
(…and the rest of the ~45-op library; the full index is in the repo map.)

## What is NOT free: behaviour

**The signatures do not tell you what a function does.** There are no doc-comments
or behavioural specs in this repo — `merge_join`'s type is just `(&[Order],&[Item])
-> Vec<Line>`; whether it multiplies quantity in, how ties are grouped, whether the
join is inner or outer, and what `bounded_add` does at the cap are **not documented**.
To compose `report` correctly you must **read the bodies** of the dependencies you
use and recover their behaviour yourself. (Types are free, behaviour is not — the
realistic maintainer situation.)

Author `report` as the smallest correct composition; run `cargo test` against the
acceptance suite before finalising.
