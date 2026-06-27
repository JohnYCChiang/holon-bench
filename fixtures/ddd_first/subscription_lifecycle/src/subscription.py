class Subscription:
    """Aggregate root modelling the subscription lifecycle state machine."""

    def __init__(self):
        self.state = "trialing"
        self.events: list[str] = []

    def activate(self) -> None:
        raise NotImplementedError("implement activate per DOMAIN.md")

    def mark_past_due(self) -> None:
        raise NotImplementedError("implement mark_past_due per DOMAIN.md")

    def cancel(self) -> None:
        raise NotImplementedError("implement cancel per DOMAIN.md")
