def escalate(incident):
    """Return the escalation target for an incident (legacy default queue)."""
    return "page:default-queue"
