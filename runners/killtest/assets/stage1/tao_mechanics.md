# Tao — mechanics

You work inside a Tao L0 store via `tao-port`. You author `report` as a typed def
node that composes existing library definitions; the kernel typechecks it and its
laws are run.

Substrate: the relational mini-store library already lives in the store as content-
addressed def nodes, each with a registered signature (a trusted `TypeOf` fact) and
≥1 law. You do **not** see op bodies; you query their **contracts**.

## Compose from the LAWS — do not read bodies

`library_index.md` already gives you, for every dependency, its **signature** and its
**law** (the complete behavioural contract — e.g. "merge_join: one Line per
(order,item) with order.item==item.id; value carried, not multiplied; grouped by key
ascending"). **The law IS the spec — that is the whole point of this substrate.**

- **Compose directly from the laws.** You do NOT need to open dependency
  implementations. There is a `node <id>` command that dumps a body, but reaching for
  it is the wrong move: the law already tells you everything the body would, and a
  body read is just wasted tokens. Use `node`/`ctx` only if a specific law is
  genuinely ambiguous for your composition — and a repeated read of the same target is
  served from cache (you already have it), so never re-fetch.

## Term grammar (you do not need to discover this — it is given here)

This is the complete JSON shape; you have everything to write `report` without
exploring. Concrete ids come from `library_index.md` (deps) and `tao-port manifest`
→ `prim_defs` (primitives like `proj1`, `proj2`, `pair2`, `tcons`, `tnil`, `ifTable`,
`intEq`, `tfold`).

- Term: `{"App":[fn, arg]}` (curried — apply args one at a time), `{"Lam":[<type>, body]}`
  (de Bruijn; `{"Var":0}` is the innermost binder), `{"Def":"<id>"}`, `{"Lit":{"Int":n}}`.
- Type (for `Lam` annotations): `{"Entry":"<int-entry-id>"}` for `Int`,
  `{"Prod":[t1,t2]}` for a pair, `{"Table":<elem-type>}` for a list/table.
- **Records are structural `Prod`:** `Order` = `Line` = `Summary` = `Prod[Int,Int]`;
  `Item` = `Prod[Int, Prod[Int,Int]]` (id, (cat, value)). Build a record with `pair2`;
  read fields with `proj1`/`proj2`.
- **`tfold(init, step, table)` is a RIGHT fold**, applied as nested `App`s; the step is
  `λelem. λacc. …` (`{"Lam":[<elemType>, {"Lam":[<accType>, body]}]}`).
- **Empty-table seed:** a bare `tnil` in `tfold`'s init (a synthesis position) is
  rejected (`E-SCHEME-PARTIAL`). Seed an empty `Table` with the idiom
  `ifTable(intEq(0,1), tcons(<dummy-elem>, tnil), tnil)`.

## How to author `report`

1. Submit your def: `tao-port txn` with
   `{"inserts":[{"schema_version":0,"payload":{"Term":<your report term>}}], ...}`.
2. Typecheck: `tao-port check <your-id> --store <store> --ctx task` → fix to `{"ok":true}`.
3. Accepted when it typechecks and the acceptance laws pass. `dashboard` consumes it.

External glue or a throwaway script cannot be a verified node the existing
consumers link against — the artifact must be a real composable def.
