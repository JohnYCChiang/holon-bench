ROLE_PERMISSIONS = {
    "viewer": frozenset({"read"}),
    "editor": frozenset({"read", "write"}),
    "admin": frozenset({"read", "write", "delete", "manage"}),
}


class AccessControl:
    """Aggregate root tracking user role assignments."""

    def __init__(self):
        self.assignments: dict[str, set[str]] = {}

    def grant(self, user: str, role: str) -> None:
        raise NotImplementedError("implement grant per DOMAIN.md")

    def revoke(self, user: str, role: str) -> None:
        raise NotImplementedError("implement revoke per DOMAIN.md")

    def can(self, user: str, permission: str) -> bool:
        raise NotImplementedError("implement can per DOMAIN.md")
