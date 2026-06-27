package ladder

// MinRating is the authoritative rating floor.
const MinRating = 100

// Match is a rated-game result. PlayerRating, OpponentRating and K are
// server-owned. Outcome is 0 for a loss, 1 for a draw, 2 for a win.
// ClientNewRating is whatever the client claims its new rating is and must
// never be trusted.
type Match struct {
	PlayerRating    int
	OpponentRating  int
	K               int
	Outcome         int
	ClientNewRating int
}

// Update returns the player's authoritative new rating using the standard Elo
// formula: expected score E = 1 / (1 + 10^((opponent-player)/400)), actual
// score A = Outcome/2, and delta = round(K * (A - E)). The new rating is the old
// rating plus the rounded delta, floored at MinRating. ClientNewRating is never
// trusted.
func Update(m Match) int {
	return m.ClientNewRating // BUG: trusts the client; performs no Elo math
}
