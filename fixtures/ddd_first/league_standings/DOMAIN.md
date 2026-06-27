# Domain: League Standings (bounded context)

Implement `src/standings.py` to satisfy these rules.

## League (aggregate root)
- Created with a list of team names. Each team starts with 0 points, 0 goals-for,
  0 goals-against.
- `record_match(home, away, home_goals, away_goals)`:
  - Both teams must be known and must differ (`ValueError` otherwise).
  - Goals must be non-negative integers (`ValueError` otherwise).
  - Scoring: win = 3 points, draw = 1 each, loss = 0. Update goals-for/against.
- `standings()` returns a list of team names ordered by: points descending, then
  goal difference (goals-for minus goals-against) descending, then name ascending.
  This ordering is fully deterministic.

Only edit `src/standings.py`.
