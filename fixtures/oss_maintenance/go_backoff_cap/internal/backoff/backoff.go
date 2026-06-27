// Package backoff computes capped exponential backoff delays.
package backoff

// Backoff produces delays base, 2*base, 4*base, ... capped at max.
type Backoff struct {
	base int64
	max  int64
}

// New returns a Backoff with the given base and max (0 < base <= max).
func New(base, max int64) *Backoff {
	return &Backoff{base: base, max: max}
}

// Delay returns the backoff for a 1-based attempt: min(base*2^(attempt-1), max).
func (b *Backoff) Delay(attempt int) int64 {
	if attempt < 1 {
		attempt = 1
	}
	d := b.base
	for i := 1; i < attempt; i++ {
		// BUG: doubles without ever capping at max, so it exceeds max and
		// overflows int64 for large attempts.
		d *= 2
	}
	return d
}
