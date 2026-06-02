def route_key(event):
    """Return a routing key for an event dictionary."""
    tenant = event.get("tenant", "")
    event_type = event.get("type", "")
    return f"{tenant}:{event_type}"
