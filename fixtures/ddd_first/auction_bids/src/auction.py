class Auction:
    """Aggregate root accepting ascending bids with a minimum increment."""

    def __init__(self, start_price: int, min_increment: int):
        if start_price < 0:
            raise ValueError("start_price must be non-negative")
        if min_increment <= 0:
            raise ValueError("min_increment must be positive")
        self.start_price = start_price
        self.min_increment = min_increment
        self.closed = False
        self.highest_bid = None
        self.highest_bidder = None
        self.events: list[str] = []

    def bid(self, bidder: str, amount: int) -> None:
        raise NotImplementedError("implement bid per DOMAIN.md")

    def close(self):
        raise NotImplementedError("implement close per DOMAIN.md")

    def winner(self):
        raise NotImplementedError("implement winner per DOMAIN.md")
