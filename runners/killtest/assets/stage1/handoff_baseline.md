# Engineering task — extend the relational mini-store (Rust environment)

You are a software engineer. Implement one deliverable in the environment described
below, using the provided commands. Work normally: read what you need, write the
implementation, run the checks, fix from failures, stop when the checks pass.

## What to build

See `task_brief.md` in this session — author `report` for the bounded relational
mini-store. The brief is the source of truth for the behaviour required.

## Your environment

See `baseline_mechanics.md` in this session for how the crate is laid out (the
machine-checked signature index you get for free, and the fact that you recover each
dependency's behaviour by reading its body). You add `pub fn report(...)` composing
the existing module functions.

## The command loop (how you interact with the crate)

Every interaction goes through one wrapped command so your work is recorded:

- **Inspect the code** — read files normally in `<DIR>/crate/` to recover behaviour.
- **Save your implementation edit** (write the file, then record it):
  `run_killtest.py wrap --run-dir <DIR> --arm baseline --category edit --file src/lib.rs`
- **Run the acceptance suite:**
  `run_killtest.py wrap --run-dir <DIR> --arm baseline --category verifier -- cargo test`

(`<DIR>` is your run directory; `<DIR>/crate/` is the Rust crate with the library,
the acceptance suite, and your implementation file.)

## Done

You are finished when `cargo test` passes the acceptance suite. Submit the smallest
correct composition; then stop.
