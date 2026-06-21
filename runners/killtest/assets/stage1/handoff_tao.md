# Engineering task — extend the relational mini-store (Tao environment)

You are a software engineer. Implement one deliverable in the environment described
below, using the provided commands. Work normally: read what you need, write the
implementation, run the checks, fix from failures, stop when the checks pass.

## What to build

See `task_brief.md` in this session — author `report` for the bounded relational
mini-store. The brief is the source of truth for the behaviour required.

## Your environment

See `tao_mechanics.md` in this session for how the store works (reading dependency
contracts, submitting a typed def, typechecking). You compose `report` from the
existing library definitions.

## The command loop (how you interact with the store)

Every store interaction goes through one wrapped command so your work is recorded:

- **Read a dependency's contract (signatures + laws):**
  `run_killtest.py wrap --run-dir <DIR> --arm tao -- ctx <target-id> --budget 4000`
- **List the world / a node:**
  `run_killtest.py wrap --run-dir <DIR> --arm tao -- manifest`
  `run_killtest.py wrap --run-dir <DIR> --arm tao -- node <id>`
- **Submit your def** (pipe the txn JSON on stdin, add `--stdin`):
  `run_killtest.py wrap --run-dir <DIR> --arm tao --stdin -- txn`
- **Typecheck your def:**
  `run_killtest.py wrap --run-dir <DIR> --arm tao -- check <your-id> --ctx task`
- **Run the acceptance laws** for your deliverable:
  `run_killtest.py wrap --run-dir <DIR> --arm tao -- law <law-id>`

(`<DIR>` is your run directory; it holds the brief, the mechanics, and your store.)

## Done

You are finished when `report` typechecks (`{"ok":true}`) and the acceptance laws
pass (`{"passed":true}`). Submit the smallest correct composition; then stop.
