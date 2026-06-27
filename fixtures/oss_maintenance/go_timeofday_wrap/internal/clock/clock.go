package clock

// AddMinutes adds delta minutes to a minute-of-day and returns the resulting
// minute-of-day in the range [0, 1440). delta may be negative or span multiple
// days; the result always wraps around midnight into [0, 1440).
func AddMinutes(minuteOfDay, delta int) int {
	// BUG: Go's % keeps the sign of the dividend, so a negative total yields a
	// negative result instead of wrapping into [0, 1440).
	return (minuteOfDay + delta) % 1440
}
