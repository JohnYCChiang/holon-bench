class Leaderboard:
    def __init__(self):
        self.scores: dict = {}

    def submit(self, player: str, score: int) -> None:
        raise NotImplementedError("implement submit per DOMAIN.md")

    def ranked(self):
        raise NotImplementedError("implement ranked per DOMAIN.md")
