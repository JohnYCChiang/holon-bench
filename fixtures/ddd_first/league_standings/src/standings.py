class League:
    def __init__(self, teams):
        self.teams = set(teams)
        self.stats = {t: {"pts": 0, "gf": 0, "ga": 0} for t in teams}

    def record_match(self, home, away, home_goals, away_goals) -> None:
        raise NotImplementedError("implement record_match per DOMAIN.md")

    def standings(self):
        raise NotImplementedError("implement standings per DOMAIN.md")
