package matchmaking

// Ticket is a queued player waiting for a match. PlayerID, MMR and EnqueueTick
// are authoritative server state.
type Ticket struct {
	PlayerID    int
	MMR         int
	EnqueueTick int
}

// FindOpponent returns the PlayerID of the best opponent for `seeker` drawn from
// `pool`, or -1 if none is acceptable. A candidate is acceptable when it is not
// the seeker and |MMR-seeker.MMR| <= maxSpread. The best candidate has the
// smallest MMR gap; ties are broken by the longest wait (lowest EnqueueTick) then
// the lowest PlayerID. The result must be deterministic regardless of pool order
// and must not mutate `pool`.
func FindOpponent(pool []Ticket, seeker Ticket, maxSpread int) int {
	for _, c := range pool {
		if c.PlayerID == seeker.PlayerID {
			continue
		}
		if c.MMR-seeker.MMR <= maxSpread { // BUG: not absolute; returns first in slice order
			return c.PlayerID
		}
	}
	return -1
}
