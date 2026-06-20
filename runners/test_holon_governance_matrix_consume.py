"""Offline tests for the governance matrix consumer/guard (M17).

These prove the M15 contract claim has teeth: a document with an unrecognized
``schema_version`` is rejected, a well-formed ``governance-matrix/v1`` document is
accepted, and shape violations (row_count mismatch, missing keys, non-ok under
``--require-ok``) are rejected. Pure and offline -- no file, subprocess, or live
process beyond an in-memory dict (CLI paths use a tmp file).
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import holon_governance_matrix_consume as consume


def valid_doc(ok: bool = True) -> dict:
    rows = [
        {"capability": "fs-write", "ok": ok},
        {"capability": "fs-read", "ok": ok},
        {"capability": "process-control", "ok": ok},
    ]
    return {
        "schema_version": "governance-matrix/v1",
        "matrix": "holon_governance_matrix",
        "ok": ok,
        "row_count": len(rows),
        "rows": rows,
    }


class VerifyTest(unittest.TestCase):
    def test_valid_v1_accepted(self) -> None:
        self.assertEqual(consume.verify(valid_doc()), [])

    def test_unrecognized_schema_version_rejected(self) -> None:
        doc = valid_doc()
        doc["schema_version"] = "governance-matrix/v2"
        errors = consume.verify(doc)
        self.assertTrue(
            any("unrecognized schema_version" in e for e in errors),
            errors,
        )

    def test_missing_schema_version_rejected(self) -> None:
        doc = valid_doc()
        del doc["schema_version"]
        self.assertNotEqual(consume.verify(doc), [])

    def test_row_count_mismatch_rejected(self) -> None:
        doc = valid_doc()
        doc["row_count"] = 2  # actual rows == 3
        errors = consume.verify(doc)
        self.assertTrue(any("row_count" in e for e in errors), errors)

    def test_missing_key_rejected(self) -> None:
        doc = valid_doc()
        del doc["rows"]
        self.assertNotEqual(consume.verify(doc), [])

    def test_non_dict_rejected(self) -> None:
        self.assertNotEqual(consume.verify([1, 2, 3]), [])

    def test_require_ok_rejects_non_ok(self) -> None:
        doc = valid_doc(ok=False)
        self.assertEqual(consume.verify(doc), [])  # well-formed: accepted by default
        self.assertNotEqual(consume.verify(doc, require_ok=True), [])  # but not ok

    def test_require_ok_accepts_ok(self) -> None:
        self.assertEqual(consume.verify(valid_doc(ok=True), require_ok=True), [])


class CliTest(unittest.TestCase):
    def _write(self, doc: object) -> pathlib.Path:
        tmp = tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        )
        json.dump(doc, tmp)
        tmp.close()
        return pathlib.Path(tmp.name)

    def test_cli_accepts_valid(self) -> None:
        path = self._write(valid_doc())
        try:
            self.assertEqual(consume.main([str(path)]), 0)
        finally:
            path.unlink()

    def test_cli_rejects_bumped_version(self) -> None:
        doc = valid_doc()
        doc["schema_version"] = "governance-matrix/v2"
        path = self._write(doc)
        try:
            self.assertEqual(consume.main([str(path)]), 1)
        finally:
            path.unlink()

    def test_cli_rejects_invalid_json(self) -> None:
        tmp = tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        )
        tmp.write("{not json")
        tmp.close()
        path = pathlib.Path(tmp.name)
        try:
            self.assertEqual(consume.main([str(path)]), 1)
        finally:
            path.unlink()

    def test_cli_require_ok_fails_on_non_ok(self) -> None:
        path = self._write(valid_doc(ok=False))
        try:
            self.assertEqual(consume.main([str(path), "--require-ok"]), 1)
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
