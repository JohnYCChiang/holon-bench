package metrics

// Counter is a monotonic counter that must be safe for concurrent use by
// multiple goroutines.
type Counter struct {
	n int64
}

// Inc increments the counter by one.
func (c *Counter) Inc() {
	c.n++
}

// Add increases the counter by delta.
func (c *Counter) Add(delta int64) {
	c.n += delta
}

// Value returns the current counter value.
func (c *Counter) Value() int64 {
	return c.n
}
