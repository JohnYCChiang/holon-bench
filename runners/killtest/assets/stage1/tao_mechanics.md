# Tao — mechanics

You work inside a Tao L0 store via `tao-port`. You author `report` as a typed def
node that composes existing library definitions; the kernel typechecks it and its
laws are run.

Substrate: the relational mini-store library already lives in the store as content-
addressed def nodes, each with a registered signature (a trusted `TypeOf` fact) and
≥1 law. You do **not** see op bodies; you query their **contracts**.

## How to read the library (this is what enters your context)

- `tao-port ctx <target> --store <store> --budget N` returns a **context bundle**:
  for each dependency, its **signature** (the typed interface) and its **laws**
  (the behavioural contract, e.g. "merge_join: one Line per (order,item) with
  order.item==item.id; value carried, not multiplied; grouped by key ascending").
  Bodies are not included — the law is the spec. This is the thin surface Tao is
  *for*: you compose against sigs + laws, never against implementations.
- The dependencies you need for `report` span the `row` / `table` / `query` / `agg`
  modules (filter-valid, sort, merge-join, group, bounded-sum, sorted-unique-insert,
  summary constructor). Their names + sigs + laws are in the bundle.

## How to author `report`

1. Submit your def as a node: `tao-port txn` with
   `{"inserts":[{"schema_version":0,"payload":{"Term":<your report term>}}], ...}`.
   Reference a dependency by its def id: `{"Def":"<id>"}`. Records are `Prod`;
   fields via `proj1/proj2`; folds via `tfold(init, step, table)` (a right fold).
2. Typecheck: `tao-port check <your-id> --store <store> --ctx task`. Fix from the
   structured diagnostics until `{"ok":true}`.
3. Your `report` is accepted when it typechecks and the acceptance laws pass
   (`tao-port law <law-id>` → `{"passed":true}`). `dashboard` consumes it.

External glue or a throwaway script cannot be a verified node the existing
consumers link against — the artifact must be a real composable def.
