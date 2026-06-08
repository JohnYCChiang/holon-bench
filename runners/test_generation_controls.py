from __future__ import annotations

import argparse
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import run_model_case
import run_track


class _FakeResponse:
    def __init__(self, body: dict) -> None:
        self._payload = json.dumps(body).encode("utf-8")

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *exc: object) -> bool:
        return False

    def read(self) -> bytes:
        return self._payload


def _completion(content: str = "ok", *, finish_reason: str = "stop", completion_tokens: int = 12) -> dict:
    return {
        "choices": [{"message": {"content": content}, "finish_reason": finish_reason}],
        "usage": {"prompt_tokens": 5, "completion_tokens": completion_tokens},
    }


class ArgParsingTests(unittest.TestCase):
    def _parse(self, extra: list[str]) -> argparse.Namespace:
        base = ["py-tool-001", "--model", "m", "--endpoint", "http://x/v1"]
        return run_model_case.build_arg_parser().parse_args(base + extra)

    def test_canonical_flag_defaults_are_none_and_600(self) -> None:
        args = self._parse([])
        self.assertIsNone(args.max_output_tokens)
        self.assertIsNone(args.thinking_budget)
        self.assertEqual(args.generation_timeout_seconds, 600.0)

    def test_canonical_flags_parse(self) -> None:
        args = self._parse(
            ["--max-output-tokens", "4096", "--thinking-budget", "768", "--generation-timeout-seconds", "120"]
        )
        self.assertEqual(args.max_output_tokens, 4096)
        self.assertEqual(args.thinking_budget, 768)
        self.assertEqual(args.generation_timeout_seconds, 120.0)

    def test_generation_max_tokens_alias_normalizes_to_max_output_tokens(self) -> None:
        args = self._parse(["--generation-max-tokens", "2048"])
        self.assertEqual(args.max_output_tokens, 2048)

    def test_module_imports_sys_for_deprecation_warning(self) -> None:
        # main() reads sys.argv to warn on the deprecated alias; guard the import.
        self.assertTrue(hasattr(run_model_case, "sys"))
        self.assertTrue(hasattr(run_track, "sys"))


class RequestPatchTests(unittest.TestCase):
    def _run(self, **kwargs: object) -> tuple[dict, dict, float]:
        captured: dict = {}
        telemetry: dict = {}

        def fake_urlopen(request: object, timeout: float | None = None):  # noqa: ANN001
            captured["data"] = json.loads(request.data.decode("utf-8"))
            captured["timeout"] = timeout
            return _FakeResponse(_completion(**kwargs.get("response", {})))

        with mock.patch.object(run_model_case.urllib.request, "urlopen", side_effect=fake_urlopen):
            run_model_case.request_patch(
                "http://x/v1",
                "m",
                "prompt",
                max_output_tokens=kwargs.get("max_output_tokens"),
                generation_timeout_seconds=kwargs.get("generation_timeout_seconds", 600.0),
                telemetry=telemetry,
            )
        return captured["data"], telemetry, captured["timeout"]

    def test_max_tokens_present_when_set(self) -> None:
        data, telemetry, _ = self._run(max_output_tokens=4096)
        self.assertEqual(data["max_tokens"], 4096)
        self.assertTrue(telemetry["max_tokens_in_request"])
        self.assertEqual(telemetry["max_output_tokens"], 4096)

    def test_max_tokens_omitted_when_none(self) -> None:
        data, telemetry, _ = self._run(max_output_tokens=None)
        self.assertNotIn("max_tokens", data)
        self.assertFalse(telemetry["max_tokens_in_request"])

    def test_timeout_is_threaded(self) -> None:
        _, _, timeout = self._run(max_output_tokens=None, generation_timeout_seconds=123.0)
        self.assertEqual(timeout, 123.0)

    def test_telemetry_records_usage_and_truncation(self) -> None:
        _, telemetry, _ = self._run(
            max_output_tokens=4096,
            response={"finish_reason": "length", "completion_tokens": 4096},
        )
        self.assertEqual(telemetry["completion_tokens"], 4096)
        self.assertEqual(telemetry["finish_reason"], "length")
        self.assertTrue(telemetry["truncated"])


class TrackForwardingTests(unittest.TestCase):
    def _args(self, **over: object) -> argparse.Namespace:
        ns = argparse.Namespace(
            model="m",
            endpoint="http://x/v1",
            protocol="artifact",
            driver="direct",
            generation_timeout_seconds=600.0,
            holon_max_iterations=100,
            holon_auto_timeout_seconds=75.0,
            max_output_tokens=None,
            thinking_budget=None,
        )
        for key, value in over.items():
            setattr(ns, key, value)
        return ns

    def _cmd(self, args: argparse.Namespace, **kw: object) -> list[str]:
        return run_track.build_generation_command(
            pathlib.Path("/runners"),
            "py-tool-001",
            args,
            root=pathlib.Path("/root"),
            patch_path=pathlib.Path("/root/reports/out.txt"),
            **kw,
        )

    def test_forwards_generation_timeout_always(self) -> None:
        cmd = self._cmd(self._args())
        self.assertIn("--generation-timeout-seconds", cmd)
        self.assertEqual(cmd[cmd.index("--generation-timeout-seconds") + 1], "600.0")

    def test_forwards_holon_aligned_controls_when_set(self) -> None:
        cmd = self._cmd(self._args(max_output_tokens=4096, thinking_budget=768))
        self.assertEqual(cmd[cmd.index("--max-output-tokens") + 1], "4096")
        self.assertEqual(cmd[cmd.index("--thinking-budget") + 1], "768")

    def test_omits_controls_when_none(self) -> None:
        cmd = self._cmd(self._args())
        self.assertNotIn("--max-output-tokens", cmd)
        self.assertNotIn("--thinking-budget", cmd)

    def test_repair_threads_previous_and_feedback(self) -> None:
        cmd = self._cmd(
            self._args(max_output_tokens=4096),
            previous_artifact=pathlib.Path("/root/reports/prev.txt"),
            feedback_error="boom",
        )
        self.assertIn("--previous-artifact", cmd)
        self.assertEqual(cmd[cmd.index("--feedback-error") + 1], "boom")
        self.assertEqual(cmd[cmd.index("--max-output-tokens") + 1], "4096")


if __name__ == "__main__":
    unittest.main()
