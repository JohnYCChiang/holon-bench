package dedup

// Dedup returns the elements of items with duplicates removed, keeping the FIRST
// occurrence of each value in input order. The result is always non-nil (an
// empty, non-nil slice for empty input). The input is not modified.
func Dedup(items []string) []string {
	out := make([]string, 0, len(items))
	for i, v := range items {
		// BUG: only collapses CONSECUTIVE duplicates (like uniq), not global ones.
		if i == 0 || items[i-1] != v {
			out = append(out, v)
		}
	}
	return out
}
