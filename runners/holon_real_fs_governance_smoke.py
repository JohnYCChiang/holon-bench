#!/usr/bin/env python3
"""Real-binary smoke for the Tao fs EffectOp witness gate (holon#7 / 394a734).

Holon#7 (merged in ``taichi/holon`` PR #8, merge commit ``394a734``) added the
external config surface for the fs permission gate (holon#5 / tao#5): the runtime
installs a ``TaoEffectOpWitnessSource`` from an on-disk witness file pointed at by
``HOLON_TAO_FS_WITNESS=<path>`` (or the ``tao.fsWitness.path`` settings key; the
env wins). This smoke drives the *real* Holon binary through the same three
configurations the offline stub smoke covers, but using the real config surface
and real witness files instead of an in-process model:

- unconfigured   ``HOLON_TAO_FS_WITNESS`` unset -> legacy ungated path: fs write
  happens; no governance failure surfaces.
- governed/admit a witness file grants the fs EffectOp (``decision: admit`` with
  a ``resultType``) -> fs write happens; passing ``fs_permission`` check.
- governed/deny  a witness file with no matching grant (missing grant) -> fs
  write blocked; failing ``fs_permission`` check; one governance failure.

Binary discovery
----------------
The smoke locates the compiled Holon binary in priority order:

1. ``HOLON_BIN`` if set -- it *wins*; no fallback is tried when it is set but
   missing/non-executable, so a bad ``HOLON_BIN`` is an explicit not-run, never a
   silent fallback to a stale build.
2. the current world layout ``../holon/target/debug/holon`` relative to the bench
   root (i.e. the sibling ``holon`` repo checkout).
3. the legacy ``/home/taichi/Migration/holon/target/debug/holon`` path, kept only
   as a documented last-resort candidate.

Diagnostics name every candidate that was checked.

Endpoint convention (provider-dependent)
-----------------------------------------
``HOLON_SMOKE_ENDPOINT`` (or ``--endpoint``) is passed to Holon as the workflow
``base_url_override``. The path Holon appends depends on the provider selected
for the model: OpenAI-compatible local providers use ``/chat/completions`` (and
often expect a base ending in one ``/v1``), while Anthropic-style providers append
``/v1/messages`` (and expect a host-level base without ``/v1``). This smoke
prints the configured base and fails unreachable endpoints before the full
three-scenario run. If the later workflow error shows a doubled path such as
``/v1/v1/messages``, choose a model/provider and base URL pair that agree.

CI / readiness behavior
-----------------------
The compiled Holon binary plus a live endpoint are not available in default CI,
so this smoke is **opt-in**:

- No usable binary, or no endpoint explicitly configured -> explicit ``not-run``
  (exit 0 by default), leaving default CI unaffected.
- ``--require-real`` turns a skip into a nonzero exit, for gating jobs that must
  fail if the real path is not exercised.
- An explicitly configured but **unreachable** endpoint fails clearly (nonzero)
  during preflight, before the three-scenario smoke runs and emits a confusing
  workflow/API artifact partway through.

The offline, binary-free coverage lives in ``holon_fs_governance_smoke.py`` and is
preserved unchanged.

Running it
----------
- Against the real binary::

      HOLON_BIN=../holon/target/debug/holon \
      HOLON_SMOKE_ENDPOINT=http://127.0.0.1:8086/v1 \
      python3 runners/holon_real_fs_governance_smoke.py .

  A live endpoint compatible with the Holon provider selected for the smoke model
  is required so the agent actually attempts the fs write the witness then gates.

- Deterministic local exercise (``--mock-endpoint``): starts a tiny in-process
  OpenAI-compatible mock so binary/endpoint preflight passes without a live model
  server. This deterministically drives the **offline stub** binary (which honors
  ``HOLON_TAO_FS_WITNESS`` and ignores the endpoint). The canned mock response is
  *not* guaranteed to drive the **real** binary to attempt the fs write, so a real
  binary still wants a real model endpoint; see the caveat in the unit tests.

- Offline rehearsal of the witness contract (no real binary, no endpoint): point
  ``HOLON_BIN`` at the offline stub shim, which honors ``HOLON_TAO_FS_WITNESS``
  by reading the same witness files. This is what the unit tests do; see
  ``runners/test_holon_real_fs_governance.py`` and
  ``.claude/tasks/holon-tao-witness-config-surface.md``.
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
import pathlib
import socket
import subprocess
import sys
import tempfile
import threading
import urllib.parse

from common import bench_root
import holon_witness

CASE_ID = "py-tool-001"
TARGET = "src/tool_errors/runner.py"
ANCHOR = "def run_tool"
MARKER = "# holon real fs-witness smoke marker: gated owned-file change.\n"
EFFECT_OP = "fs.edit"

# Binary discovery candidates (HOLON_BIN, when set, wins over both of these).
WORLD_HOLON_BIN_REL = pathlib.PurePosixPath("../holon/target/debug/holon")
LEGACY_HOLON_BIN = pathlib.Path("/home/taichi/Migration/holon/target/debug/holon")
# Placeholder used only to report an unconfigured endpoint; never contacted.
DEFAULT_ENDPOINT = "http://127.0.0.1:1/v1"


def binary_candidates(root: pathlib.Path) -> list[tuple[str, pathlib.Path]]:
    """Ordered (label, path) candidates for the real Holon binary.

    ``HOLON_BIN`` *wins*: when set it is the only candidate, so a bad value is a
    clear not-run rather than a silent fallback to a stale build. Otherwise the
    current world layout is tried first and the legacy path last.
    """
    env = os.environ.get("HOLON_BIN")
    if env:
        return [("HOLON_BIN", pathlib.Path(env))]
    return [
        ("world-layout", (root / WORLD_HOLON_BIN_REL).resolve()),
        ("legacy", LEGACY_HOLON_BIN),
    ]


def resolve_binary(
    root: pathlib.Path | None = None,
) -> tuple[pathlib.Path | None, list[str]]:
    """Return ``(binary_or_None, diagnostics)`` over the discovery candidates."""
    if root is None:
        root = bench_root(".")
    diagnostics: list[str] = []
    for label, path in binary_candidates(root):
        if path.is_file() and os.access(path, os.X_OK):
            diagnostics.append(f"{label}={path} [OK]")
            return path, diagnostics
        why = "missing" if not path.exists() else "not executable"
        diagnostics.append(f"{label}={path} [{why}]")
    return None, diagnostics


def resolve_endpoint(cli_endpoint: str | None) -> tuple[str, bool]:
    """Return ``(endpoint, explicitly_configured)``.

    Explicit means ``--endpoint`` was passed or ``HOLON_SMOKE_ENDPOINT`` is set;
    otherwise the placeholder is returned and the caller treats it as not-run.
    """
    if cli_endpoint:
        return cli_endpoint.strip(), True
    env = os.environ.get("HOLON_SMOKE_ENDPOINT", "").strip()
    if env:
        return env, True
    return DEFAULT_ENDPOINT, False


def endpoint_reachable(endpoint: str, timeout: float = 3.0) -> tuple[bool, str]:
    """Best-effort TCP preflight; distinguishes unreachable from a real run."""
    parsed = urllib.parse.urlparse(endpoint)
    host = parsed.hostname
    if not host:
        return False, f"unparseable endpoint {endpoint!r}"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"{host}:{port} reachable"
    except OSError as exc:
        return False, f"{host}:{port} unreachable ({exc})"


class _MockOpenAIHandler(http.server.BaseHTTPRequestHandler):
    """Minimal OpenAI-compatible chat-completions responder for --mock-endpoint."""

    def do_POST(self) -> None:  # noqa: N802 (http.server API)
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length:
            self.rfile.read(length)
        body = json.dumps(
            {
                "id": "mock-holon-smoke",
                "object": "chat.completion",
                "model": "mock",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": ""},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
            }
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *args: object) -> None:  # silence request logging
        pass


def start_mock_endpoint() -> tuple[http.server.ThreadingHTTPServer, str]:
    """Start a local mock endpoint on an ephemeral port; return (server, base_url)."""
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _MockOpenAIHandler)
    except OSError as exc:
        raise RuntimeError(f"mock endpoint unavailable: {exc}") from exc
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[0], server.server_address[1]
    return server, f"http://{host}:{port}/v1"


def run(command: list[str], root: pathlib.Path, env: dict[str, str]) -> None:
    completed = subprocess.run(
        command, cwd=root, text=True, capture_output=True, check=False, env=env
    )
    if completed.returncode not in (0, 1):
        # 0 = case passed, 1 = case failed its verifier (expected on a deny).
        # Anything else is a harness/crash failure we must surface.
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def run_scenario(
    root: pathlib.Path,
    holon_bin: pathlib.Path,
    endpoint: str,
    temp_root: pathlib.Path,
    label: str,
    witness_path: pathlib.Path | None,
) -> tuple[str, dict, dict]:
    artifact = temp_root / f"{label}_artifact.txt"
    result = temp_root / f"{label}_result.json"
    score = temp_root / f"{label}_score.json"

    env = os.environ.copy()
    env["HOLON_BIN"] = str(holon_bin)
    env["HOLON_STUB_TARGET"] = TARGET
    env["HOLON_STUB_ANCHOR"] = ANCHOR
    env["HOLON_STUB_MARKER"] = MARKER
    env["HOLON_STUB_CASE"] = CASE_ID
    env["HOLON_STUB_FS_EFFECT_OP"] = EFFECT_OP
    # The real config surface: env points at the on-disk witness file. Unset
    # means legacy ungated. Never lean on the in-process HOLON_STUB_FS_WITNESS
    # model here -- this smoke exercises the real witness file path only.
    env.pop("HOLON_STUB_FS_WITNESS", None)
    if witness_path is not None:
        env["HOLON_TAO_FS_WITNESS"] = str(witness_path)
    else:
        env.pop("HOLON_TAO_FS_WITNESS", None)

    model = f"holon-real-fs-{label}"
    run(
        [
            sys.executable,
            str(root / "runners" / "run_model_case.py"),
            CASE_ID,
            "--model",
            model,
            "--driver",
            "holon-cli",
            "--protocol",
            "artifact",
            "--endpoint",
            endpoint,
            "--bench-root",
            str(root),
            "--out",
            str(artifact),
        ],
        root,
        env,
    )
    run(
        [
            sys.executable,
            str(root / "runners" / "run_case.py"),
            CASE_ID,
            "--model",
            model,
            "--artifact-file",
            str(artifact),
            "--bench-root",
            str(root),
            "--work-root",
            str(temp_root / f"{label}_work"),
            "--out",
            str(result),
        ],
        root,
        env,
    )
    run(
        [
            sys.executable,
            str(root / "runners" / "score_case.py"),
            str(result),
            "--bench-root",
            str(root),
            "--out",
            str(score),
        ],
        root,
        env,
    )
    return (
        artifact.read_text(encoding="utf-8"),
        json.loads(result.read_text(encoding="utf-8")),
        json.loads(score.read_text(encoding="utf-8")),
    )


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(f"holon_real_fs_governance_smoke: {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bench_root", nargs="?", default=".")
    parser.add_argument(
        "--endpoint",
        default=None,
        help=(
            "Provider-compatible base URL (live model needed). Defaults to "
            "HOLON_SMOKE_ENDPOINT; unset means not-run. For local OpenAI-compatible "
            "providers this usually ends in /v1; Anthropic-style providers append "
            "/v1/messages and usually expect a host-level base."
        ),
    )
    parser.add_argument(
        "--require-real",
        action="store_true",
        help="Exit nonzero (instead of 0) when the real smoke is skipped.",
    )
    parser.add_argument(
        "--mock-endpoint",
        action="store_true",
        help=(
            "Start a local deterministic OpenAI-compatible mock endpoint so "
            "binary/endpoint preflight passes without a live model server."
        ),
    )
    args = parser.parse_args()

    root = bench_root(args.bench_root)
    holon_bin, bin_diag = resolve_binary(root)

    mock_server: http.server.ThreadingHTTPServer | None = None
    if args.mock_endpoint:
        try:
            mock_server, endpoint = start_mock_endpoint()
        except RuntimeError as exc:
            print(
                "holon_real_fs_governance_smoke: not-run "
                f"({exc}; local socket binding is required for --mock-endpoint). "
                "Offline coverage: runners/holon_fs_governance_smoke.py."
            )
            return 1 if args.require_real else 0
        endpoint_explicit = True
        endpoint_source = "--mock-endpoint"
    else:
        endpoint, endpoint_explicit = resolve_endpoint(args.endpoint)
        endpoint_source = (
            "--endpoint"
            if args.endpoint
            else "HOLON_SMOKE_ENDPOINT"
            if endpoint_explicit
            else "unset"
        )

    try:
        skip_reasons: list[str] = []
        if holon_bin is None:
            skip_reasons.append(
                "no executable Holon binary [checked: " + "; ".join(bin_diag) + "]"
            )
        if not endpoint_explicit:
            skip_reasons.append(
                "no endpoint configured (set HOLON_SMOKE_ENDPOINT=http://host:port/v1, "
                "pass --endpoint, or use --mock-endpoint)"
            )

        if skip_reasons:
            print(
                "holon_real_fs_governance_smoke: not-run ("
                + "; ".join(skip_reasons)
                + "). Offline coverage: runners/holon_fs_governance_smoke.py."
            )
            return 1 if args.require_real else 0

        assert holon_bin is not None  # narrowed by skip_reasons above
        print(
            "holon_real_fs_governance_smoke: binary="
            f"{holon_bin}; endpoint={endpoint} (source: {endpoint_source}); "
            "provider-specific request path will be appended by Holon"
        )
        if "/v1/v1" in endpoint:
            print(
                "holon_real_fs_governance_smoke: warning: endpoint contains "
                "'/v1/v1'; pass the provider base URL, not a fully doubled path."
            )

        reachable, why = endpoint_reachable(endpoint)
        if not reachable:
            print(
                "holon_real_fs_governance_smoke: FAIL endpoint preflight: "
                f"{why}. Configure a live OpenAI-compatible endpoint (base URL "
                "matching the selected Holon provider) or use --mock-endpoint for "
                "a deterministic local run."
            )
            return 1

        return _run_scenarios(root, holon_bin, endpoint)
    finally:
        if mock_server is not None:
            mock_server.shutdown()
            mock_server.server_close()


def _run_scenarios(
    root: pathlib.Path, holon_bin: pathlib.Path, endpoint: str
) -> int:
    with tempfile.TemporaryDirectory(prefix="holon-bench-real-fs-smoke-") as temp:
        temp_root = pathlib.Path(temp)

        # unconfigured / legacy ungated: no witness file -> baseline allow.
        ungov_art, ungov_res, ungov_score = run_scenario(
            root, holon_bin, endpoint, temp_root, "unconfigured", witness_path=None
        )
        check(
            MARKER.strip() in ungov_art,
            "unconfigured did not preserve baseline allow (legacy ungated)",
        )
        check(
            ungov_res.get("governance_mode") != "governed",
            "unconfigured run was unexpectedly governed",
        )
        check(
            ungov_score.get("governance_failure_count") == 0,
            "unconfigured run unexpectedly recorded a governance failure",
        )

        # governed/admit: witness grants the fs EffectOp.
        admit_witness = holon_witness.write_witness(
            temp_root / "admit_witness.json",
            [holon_witness.admit_grant(EFFECT_OP, TARGET, result_type="Patch")],
        )
        admit_art, admit_res, admit_score = run_scenario(
            root, holon_bin, endpoint, temp_root, "admit", witness_path=admit_witness
        )
        check(MARKER.strip() in admit_art, "governed/admit did not allow the fs write")
        check(
            admit_res.get("governance_mode") == "governed",
            "governed/admit run was not labeled governed",
        )
        admit_checks = {c["name"]: c for c in admit_res.get("governance_checks") or []}
        check(
            admit_checks.get("fs_permission", {}).get("passed") is True,
            "governed/admit did not record a passing fs_permission check",
        )
        check(
            admit_score.get("governance_failure_count") == 0,
            "governed/admit unexpectedly recorded a governance failure",
        )

        # governed/deny: witness with no matching grant -> missing-grant deny.
        # A well-formed file whose only grant targets a different EffectOp, so the
        # fs.edit op has no matching row and fails closed.
        deny_witness = holon_witness.write_witness(
            temp_root / "deny_witness.json",
            [holon_witness.admit_grant("fs.delete", TARGET, result_type="Unit")],
        )
        deny_art, deny_res, deny_score = run_scenario(
            root, holon_bin, endpoint, temp_root, "deny", witness_path=deny_witness
        )
        check(
            MARKER.strip() not in deny_art,
            "governed/deny did NOT block the fs write (baseline leaked through)",
        )
        check(
            deny_res.get("governance_mode") == "governed",
            "governed/deny run was not labeled governed",
        )
        deny_checks = {c["name"]: c for c in deny_res.get("governance_checks") or []}
        check(
            deny_checks.get("fs_permission", {}).get("passed") is False,
            "governed/deny did not record a failing fs_permission check",
        )
        check(
            deny_score.get("governance_failure_count") == 1,
            "governed/deny did not record exactly one governance failure",
        )
        chain = deny_res.get("tao_truth_chain") or {}
        check(
            chain.get("subject_id") == f"case::{CASE_ID}",
            "governed/deny did not surface the Tao truth chain",
        )

    print(
        "holon_real_fs_governance_smoke: ok "
        "(real binary via HOLON_TAO_FS_WITNESS: unconfigured allow vs "
        "governed admit/deny)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
