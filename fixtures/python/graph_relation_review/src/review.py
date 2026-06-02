def review_change(change):
    """Return review warnings for a proposed account change."""
    warnings = []
    if change.get("amount", 0) < 0:
        warnings.append("negative amount")
    return warnings
