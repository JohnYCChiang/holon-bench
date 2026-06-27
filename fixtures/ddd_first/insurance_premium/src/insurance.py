class InsurancePolicy:
    CLAIM_SURCHARGE = 5000

    def __init__(self, base_cents: int):
        if base_cents <= 0:
            raise ValueError("base must be positive")
        self.base_cents = base_cents

    def quote(self, age: int, prior_claims: int, loyalty_years: int) -> int:
        raise NotImplementedError("implement quote per DOMAIN.md")
