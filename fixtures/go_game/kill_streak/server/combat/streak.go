package combat

// Tracker holds authoritative per-player kill streaks. A streak counts kills
// since the player last died; the best streak never decreases.
type Tracker struct {
	cur  map[string]int
	best map[string]int
}

func NewTracker() *Tracker {
	return &Tracker{cur: map[string]int{}, best: map[string]int{}}
}

// Kill increments the player's current streak and updates their best.
func (t *Tracker) Kill(id string) {
	t.cur[id]++
	if t.cur[id] > t.best[id] {
		t.best[id] = t.cur[id]
	}
}

// Death ends the current streak, resetting it to zero. The best streak is kept.
func (t *Tracker) Death(id string) {
	// BUG: a death must reset the current streak but this leaves it intact.
}

func (t *Tracker) Current(id string) int { return t.cur[id] }
func (t *Tracker) Best(id string) int    { return t.best[id] }
