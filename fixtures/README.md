# Fixtures

Phase 1 case manifests are intentionally created before full fixture workspaces.
Each fixture path named by a case should become a self-contained git workspace
with failing tests and deterministic verifier commands.

Fixture contract:

- Must be copyable to a temporary workspace.
- Must contain only files needed by the case.
- Must include baseline tests and hidden or verifier tests where applicable.
- Must not rely on external services.
- Must keep resource use bounded by the case timeout.
