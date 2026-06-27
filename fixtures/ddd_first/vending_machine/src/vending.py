class VendingMachine:
    def __init__(self, inventory: dict):
        self.inventory = dict(inventory)
        self.denoms_desc = sorted(self.inventory, reverse=True)

    def dispense_change(self, amount: int) -> dict:
        raise NotImplementedError("implement dispense_change per DOMAIN.md")
