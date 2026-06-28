package ready

// Check gates a match start behind an all-players-ready condition. A match may
// start only when at least one player has joined and every joined player is
// ready.
type Check struct {
	ready map[string]bool
}

func NewCheck() *Check { return &Check{ready: map[string]bool{}} }

// Join registers a player who is initially not ready. Re-joining keeps the
// existing ready state.
func (c *Check) Join(id string) {
	if id == "" {
		return
	}
	if _, ok := c.ready[id]; !ok {
		c.ready[id] = false
	}
}

// SetReady marks a joined player ready. Unknown players are ignored.
func (c *Check) SetReady(id string) {
	if _, ok := c.ready[id]; ok {
		c.ready[id] = true
	}
}

// AllReady reports whether the match may start.
func (c *Check) AllReady() bool {
	return len(c.ready) > 0 // BUG: starts as soon as anyone joins, ignoring ready state.
}
