package hitreg

type Pos struct {
	Tick int
	X, Y int
}

type History struct {
	max int
	buf []Pos
}

func NewHistory(max int) *History { return &History{max: max} }

// Record stores the target's authoritative position for a tick. Ticks are
// recorded in ascending order; only the most recent max ticks are retained.
func (h *History) Record(p Pos) {
	h.buf = append(h.buf, p)
	if len(h.buf) > h.max {
		h.buf = h.buf[len(h.buf)-h.max:]
	}
}

// PositionAt returns the recorded position for exactly the given tick. ok is
// false when that tick is not in the retained window: the server never
// extrapolates or trusts a client-supplied position.
func (h *History) PositionAt(tick int) (Pos, bool) {
	if len(h.buf) == 0 {
		return Pos{}, false
	}
	return h.buf[len(h.buf)-1], true
}

// ValidateHit accepts a client's hit claim only if the target's rewound position
// at claimTick is within radius of the shot. The client's own claimed position
// is never trusted.
func (h *History) ValidateHit(claimTick, shotX, shotY, radius int) bool {
	p, ok := h.PositionAt(claimTick)
	if !ok {
		return false
	}
	dx, dy := p.X-shotX, p.Y-shotY
	return dx*dx+dy*dy <= radius*radius
}
