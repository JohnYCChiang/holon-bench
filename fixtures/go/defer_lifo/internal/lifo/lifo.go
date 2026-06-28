package lifo

// Shutdown registers each name for deferred close in registration order and
// returns the names in the order they were actually closed. Deferred calls run
// in last-in-first-out order, so the result must be the reverse of names.
func Shutdown(names []string) []string {
	order := []string{}
	record := func(n string) { order = append(order, n) }
	for _, n := range names {
		defer record(n)
	}
	return order
}
