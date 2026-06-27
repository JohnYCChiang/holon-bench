# Domain: Leaderboard Ranking (bounded context)

Implement `src/leaderboard.py` to satisfy these rules.

## Leaderboard (aggregate root)
- Starts empty. Each player has at most one score.
- `submit(player, score)`: `score` must be a non-negative integer (`ValueError`).
  Submitting a player that already has a score is a domain error (`ValueError`); a
  rejected command must not mutate state.
- `ranked()` returns a list of `(rank, player, score)` tuples using STANDARD COMPETITION
  RANKING ("1224"): entries are ordered by score descending, then player name ascending;
  players with equal scores share the same rank, and the next distinct score's rank is
  its 1-based position (so ranks skip after ties).

Only edit `src/leaderboard.py`.
