package filter

// Filter returns the elements of in for which keep returns true.
// The result must always be non-nil so JSON encoding produces [] not null.
func Filter(in []int, keep func(int) bool) []int {
	var out []int
	for _, v := range in {
		if keep(v) {
			out = append(out, v)
		}
	}
	return out
}
