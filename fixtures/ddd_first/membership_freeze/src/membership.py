class Membership:
    MAX_FREEZE = 3

    def __init__(self):
        self.state = "ACTIVE"
        self.frozen_used = 0
        self.events: list = []

    def freeze(self, months: int) -> None:
        raise NotImplementedError("implement freeze per DOMAIN.md")

    def unfreeze(self) -> None:
        raise NotImplementedError("implement unfreeze per DOMAIN.md")
