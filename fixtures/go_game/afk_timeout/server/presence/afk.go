package presence

type Tracker struct {
	timeout int
	last    map[string]int
}

func NewTracker(timeout int) *Tracker {
	return &Tracker{timeout: timeout, last: map[string]int{}}
}

// Touch records activity for a player at the given tick (non-decreasing clock).
func (t *Tracker) Touch(id string, tick int) {
	if t.last == nil {
		t.last = map[string]int{}
	}
	t.last[id] = tick
}

// Sweep returns the sorted ids of players idle for at least timeout ticks at now
// (now-last >= timeout, so the boundary is inclusive). Swept players are removed
// from tracking and will not be returned again until they Touch once more.
func (t *Tracker) Sweep(now int) []string {
	var out []string
	for id, last := range t.last {
		if now-last > t.timeout {
			out = append(out, id)
		}
	}
	return out
}
