package limiter

// Limiter is a sliding-window rate limiter. It admits at most capacity events
// within any window of `window` ticks. An event recorded at time t is in-window
// at time now while now-t < window; once now-t >= window it has expired and no
// longer counts toward capacity.
type Limiter struct {
	capacity int
	window   int64
	events   []int64
}

// New returns a limiter allowing capacity events per window ticks.
func New(capacity int, window int64) *Limiter {
	return &Limiter{capacity: capacity, window: window}
}

// Allow reports whether an event at time now is admitted, recording it on
// success. now must be non-decreasing across calls.
func (l *Limiter) Allow(now int64) bool {
	kept := l.events[:0]
	for _, t := range l.events {
		if now-t > l.window { // BUG: should be >= ; an event exactly window ticks old must expire
			continue
		}
		kept = append(kept, t)
	}
	l.events = kept
	if len(l.events) >= l.capacity {
		return false
	}
	l.events = append(l.events, now)
	return true
}
