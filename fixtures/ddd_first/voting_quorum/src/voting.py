class Poll:
    """Aggregate root: one vote per eligible voter, quorum-gated result."""

    def __init__(self, eligible, options, quorum: int):
        if not isinstance(quorum, int) or quorum <= 0:
            raise ValueError("quorum must be a positive integer")
        self.eligible = set(eligible)
        self.options = list(options)
        self.quorum = quorum
        self.votes: dict = {}
        self.closed = False

    def cast(self, voter, option) -> None:
        raise NotImplementedError("implement cast per DOMAIN.md")

    def close(self) -> None:
        raise NotImplementedError("implement close per DOMAIN.md")

    def tally(self) -> dict:
        raise NotImplementedError("implement tally per DOMAIN.md")

    def result(self):
        raise NotImplementedError("implement result per DOMAIN.md")
