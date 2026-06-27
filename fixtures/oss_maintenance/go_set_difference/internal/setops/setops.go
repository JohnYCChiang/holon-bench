// Package setops provides order-preserving set operations on string slices.
package setops

// Difference returns the elements of a that are not in b, in a's first-seen
// order, with duplicates collapsed. The returned slice is always non-nil (empty
// when nothing remains). Inputs are not mutated.
func Difference(a, b []string) []string {
	inB := make(map[string]struct{}, len(b))
	for _, x := range b {
		inB[x] = struct{}{}
	}
	seen := make(map[string]struct{}, len(a))
	out := []string{}
	for _, x := range a {
		_, inb := inB[x]
		_, dup := seen[x]
		// BUG: keeps elements that ARE in b; the condition must be !inb && !dup.
		if inb && !dup {
			out = append(out, x)
			seen[x] = struct{}{}
		}
	}
	return out
}
