from dataclasses import dataclass


@dataclass(frozen=True)
class PasswordPolicy:
    """Value object describing password strength rules."""

    min_length: int
    require_digit: bool = False
    require_symbol: bool = False

    SYMBOLS = "!@#$%^&*"

    def violations(self, password: str) -> tuple:
        raise NotImplementedError("implement violations per DOMAIN.md")

    def is_valid(self, password: str) -> bool:
        raise NotImplementedError("implement is_valid per DOMAIN.md")


class Credential:
    """Aggregate root applying a PasswordPolicy with no password reuse."""

    def __init__(self, policy: PasswordPolicy):
        self.policy = policy
        self.password = None
        self.history: list[str] = []
        self.events: list[str] = []

    def set_password(self, pw: str) -> None:
        raise NotImplementedError("implement set_password per DOMAIN.md")
