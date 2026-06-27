class RefundPolicy:
    SERVICE_FEE = 500

    def refund(self, price_cents: int, days_before: int) -> int:
        raise NotImplementedError("implement refund per DOMAIN.md")
