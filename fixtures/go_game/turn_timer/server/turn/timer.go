package turn

// Game runs an authoritative turn timer. Players act in a fixed rotation; each
// turn lasts limit ticks. Only the current player may act, and only before the
// turn deadline. Turns advance deterministically whether a player acts or is
// timed out.
type Game struct {
	order    []string
	idx      int
	deadline int64
	limit    int64
}

func NewGame(order []string, start int64, limit int64) *Game {
	return &Game{order: order, deadline: start + limit, limit: limit}
}

// Current returns the player whose turn it is.
func (g *Game) Current() string {
	if len(g.order) == 0 {
		return ""
	}
	return g.order[g.idx%len(g.order)]
}

// Act applies player's action at tick now. It is accepted only if player is the
// current player and now is before the deadline; on success the turn advances.
func (g *Game) Act(player string, now int64) bool {
	// BUG: trusts the client; accepts any player at any time and advances.
	g.idx++
	g.deadline += g.limit
	return true
}

// Tick advances past any turns whose deadline has passed at tick now.
func (g *Game) Tick(now int64) {
	for now >= g.deadline {
		g.idx++
		g.deadline += g.limit
	}
}
