# Domain: Voting (bounded context)

Implement `src/voting.py`. A `Poll` collects one vote per eligible voter, can be
closed, and reports a deterministic result only once quorum is reached.

## Poll (aggregate root)
- Created with an iterable of `eligible` voter ids, an ordered iterable of
  `options`, and a positive integer `quorum`.
  - Invariant: `quorum` is a positive integer (`ValueError` otherwise).
  - The declared option order is retained and used for deterministic tie-breaks.
- `cast(voter, option)` records a vote.
  - Invariant: the poll must be open (`ValueError` once closed).
  - Invariant: `voter` must be eligible (`ValueError` otherwise).
  - Invariant: `option` must be a declared option (`ValueError` otherwise).
  - Invariant: one vote per voter — a second vote by the same voter is rejected
    and must not mutate state.
- `close()` closes the poll; further `cast` is rejected.
- `tally()` returns a dict mapping every declared option to its vote count
  (0 for options with no votes). Allowed at any time.
- `result()` returns the winning option.
  - Invariant: the poll must be closed (`ValueError` otherwise).
  - Invariant: total votes cast must be `>= quorum` (`ValueError` otherwise).
  - The winner is the option with the most votes; ties are broken in favour of
    the option declared earliest.

Only edit `src/voting.py`.
