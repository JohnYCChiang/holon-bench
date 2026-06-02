from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.redaction_tool.redact import redact_output


def main() -> None:
    text = "\n".join(
        [
            "token=alpha",
            "callback=https://example.invalid/?api_key=query-secret",
            "Bearer mixedCaseSecret",
        ]
    )
    result = redact_output(text, preview_lines=2)
    assert result["line_count"] == 3
    assert result["byte_count"] == len(text.encode("utf-8"))
    assert result["redaction_count"] >= 3
    rendered = result["redacted"] + "\n" + result["preview"]
    for secret in ("alpha", "query-secret", "mixedCaseSecret"):
        assert secret not in rendered


if __name__ == "__main__":
    main()
