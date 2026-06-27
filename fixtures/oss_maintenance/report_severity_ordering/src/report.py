def render_report(findings):
    """Render findings as ``"<severity>:<name>"`` lines.

    Ordering contract: highest severity first; ties broken by name ascending.
    ``severity`` is an integer. The input list must not be mutated.
    """
    ordered = sorted(findings, key=lambda f: (str(f["severity"]), f["name"]), reverse=True)
    return [f"{f['severity']}:{f['name']}" for f in ordered]
