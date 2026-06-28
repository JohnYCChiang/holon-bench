def resource_name(spec):
    """Return a resource name (legacy: the bare name)."""
    return spec.get("name", "")
