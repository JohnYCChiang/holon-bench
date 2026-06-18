# Kill-test Stage-1 readiness

Status: completed for `holon-bench#18`.

This note records the safe readiness audit for the Tao kill-test harness. It is
not a formal SortedUniqList experiment result. No private-suite content is
copied into this repository, no prereg threshold is changed, and no
`LEGISLATOR_CONFIRMED.json` sentinel is created by this audit.

## Safe probes

The readiness pass ran only shakedown and harness-health commands:

- `python3 runners/run_killtest.py --help`
- `python3 runners/run_killtest.py selftest`
- `python3 runners/run_killtest.py hashes`
- `python3 runners/run_killtest.py decoy`
- `python3 runners/run_killtest.py checklist --mounts ../runs/tao-killtest/decoy/tao ../runs/tao-killtest/decoy/baseline`

Observed results:

- CLI help lists the expected kill-test commands.
- `selftest` passed 22/22 pure harness checks.
- `hashes` produced acceptance and hidden suite SHA-256 hashes from the local
  private-suite path.
- `decoy` completed both arms under `../runs/tao-killtest/decoy`.
- `checklist` reported `gate_pass: true` using existing run-root evidence,
  including committed suite hashes, pinned model id, signed toolchain registry,
  clean leak scan, and an already-present Legislator sentinel.

## Formal experiment boundary

The readiness pass does not start or score a formal experiment. A formal run
must still be driven through the preregistered operator flow in
`docs/killtest-harness.md`, using the existing gate evidence rather than
fabricating it.

The decoy output is a shakedown artifact only. It confirms that the harness can
exercise both arms without touching the registered task or private hidden suite
inside arm-visible mounts.

## Validation

Additional validation run for this readiness record:

- `python3 runners/schema_check.py .`
- `python3 -m py_compile runners/*.py`
- `python3 runners/docs_check.py .`
- `python3 runners/ci_smoke.py .`
- `./scripts/check_world.sh` from the world root
