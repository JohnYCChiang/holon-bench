# Domain: Access Control (bounded context)

Implement `src/access.py` to satisfy these rules.

## Roles and permissions (value mapping)
Three roles grant fixed permission sets (provided as `ROLE_PERMISSIONS`):
- `"viewer"`  -> {`"read"`}
- `"editor"`  -> {`"read"`, `"write"`}
- `"admin"`   -> {`"read"`, `"write"`, `"delete"`, `"manage"`}

## AccessControl (aggregate root)
- Tracks which roles each user holds. Starts with no assignments.
- `grant(user, role)` assigns a role to a user.
  - Invariant: `role` must be one of the known roles (`ValueError` otherwise).
  - Granting a role a user already holds is idempotent (no duplication, no error).
- `revoke(user, role)` removes a role from a user.
  - Invariant: the user must currently hold that role (`ValueError` otherwise).
  - Invariant: while any admin exists, the system must retain at least one user
    holding `"admin"` — revoking the last admin is a domain error (`ValueError`).
    A rejected command must not mutate state.
- `can(user, permission)` returns True when any role the user holds grants the
  permission. Unknown users can do nothing.

Only edit `src/access.py`.
