"""Tao Stage 0 kill-test harness (spike plan P4 / Appendix B).

This package adapts Holon-Bench to run the pre-registered Tao Stage 0 kill test
described in ``tao/docs/tao-killtest-prereg-v0.md`` (FROZEN). The harness
*implements* the frozen pre-registration; it never reinterprets it. Every metric
definition and decision-rule threshold is transcribed from that document with a
``prereg_ref`` citation, and the prereg file hash is recorded into the run log so
any drift from the frozen text is detectable (NT-15 discipline).

Scope: holon-bench only. Nothing here edits ``tao/`` or ``holon/``.
"""

__all__ = ["config"]
