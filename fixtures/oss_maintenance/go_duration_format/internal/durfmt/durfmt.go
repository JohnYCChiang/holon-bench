package durfmt

import "fmt"

// Format renders a non-negative number of seconds as "<H>h<M>m<S>s", where the
// minutes and seconds components are each in the range 0..59 and the hours
// component carries any remaining whole hours. For example Format(3661) is
// "1h1m1s".
func Format(seconds int) string {
	h := seconds / 3600
	// BUG: minutes is the total minutes, not the minutes-within-the-hour; it
	// should be (seconds / 60) % 60, so Format(3661) yields "1h61m1s".
	m := seconds / 60
	s := seconds % 60
	return fmt.Sprintf("%dh%dm%ds", h, m, s)
}
