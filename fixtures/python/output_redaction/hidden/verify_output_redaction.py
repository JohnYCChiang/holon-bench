from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.redaction_tool.redact import redact_output


def main() -> None:
    text = "\n".join(
        [
            "start",
            "Authorization: Bearer opaque-session-token",
            "secret_token=do-not-leak",
            "end",
        ]
    )
    result = redact_output(text, preview_lines=4)
    assert result["line_count"] == 4
    assert result["byte_count"] == len(text.encode("utf-8"))
    assert result["redaction_count"] >= 2
    rendered = result["redacted"] + "\n" + result["preview"]
    assert "opaque-session-token" not in rendered
    assert "do-not-leak" not in rendered
    assert "[REDACTED]" in result["preview"]


if __name__ == "__main__":
    main()
