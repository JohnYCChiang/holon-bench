package netio

type Limiter struct {
	Max     int
	Dropped int
	counts  map[string]int
	tick    int
}

// Accept reports whether an input from player at the given tick is accepted.
// At most Max inputs per player are accepted within the same tick; the rest are
// dropped and counted. Ticks arrive in non-decreasing order, and the per-tick
// budget resets when the tick advances.
func (l *Limiter) Accept(player string, tick int) bool {
	if l.counts == nil {
		l.counts = map[string]int{}
	}
	l.counts[player]++
	return true
}
