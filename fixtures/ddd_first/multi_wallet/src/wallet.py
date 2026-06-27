class Wallet:
    def __init__(self):
        self.balances: dict = {}

    def balance(self, currency: str) -> int:
        return self.balances.get(currency, 0)

    def deposit(self, currency: str, amount: int) -> None:
        raise NotImplementedError("implement deposit per DOMAIN.md")

    def withdraw(self, currency: str, amount: int) -> None:
        raise NotImplementedError("implement withdraw per DOMAIN.md")

    def transfer(self, other: "Wallet", currency: str, amount: int) -> None:
        raise NotImplementedError("implement transfer per DOMAIN.md")
