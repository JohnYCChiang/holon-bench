from __future__ import annotations


def interleave(events):
    stdout = [e for e in events if e["stream"] == "stdout"]
    stderr = [e for e in events if e["stream"] == "stderr"]
    ordered = stdout + stderr
    transcript = [{"stream": e["stream"], "text": e["text"]} for e in ordered]
    return {
        "ok": True,
        "transcript": transcript,
        "stdout_bytes": sum(len(e["text"]) for e in stdout),
        "stderr_bytes": sum(len(e["text"]) for e in stderr),
    }
