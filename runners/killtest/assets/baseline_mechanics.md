# Baseline arm — mechanics (token cost counts into M1/M2)

You work in a normal git text repo with an Aider-grade repo map. Per prereg §5
the tokens of this document are counted into the edit-cycle accounting, exactly
as the Tao arm's mechanics doc is.

Substrate: a Rust crate skeleton lives in your run dir. The acceptance suite
(`acceptance/rust/tests.rs`) is included as `#[cfg(test)] mod tests;` next to your
implementation. A held-out hidden + mutation suite runs at scoring time (never
shown to you).

## Repo map

```
<crate>/
  Cargo.toml
  src/
    lib.rs        # your implementation goes here
    tests.rs      # acceptance rendition (do not edit)
```

## Interface under test

```rust
pub struct SortedUniqList { /* your representation */ }
pub fn empty() -> SortedUniqList;
pub fn insert(x: i64, s: &SortedUniqList) -> SortedUniqList;
pub fn member(x: i64, s: &SortedUniqList) -> bool;
pub fn size(s: &SortedUniqList) -> usize;
```

## Command surface

- edit files under `src/` (your *edit* primitive);
- `cargo test` — runs the acceptance suite (your verifier);
- `cargo build` — typecheck/compile without running tests.

Do not edit `src/tests.rs` or weaken any assertion. Green = `cargo test` passes
with the acceptance suite. Make the smallest correct change.
