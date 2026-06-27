package bitset

// PopCount returns the number of 1 bits in x.
func PopCount(x uint64) int {
	count := 0
	// BUG: only inspects the low 32 bits, so any set bit at position 32..63 is
	// never counted (e.g. PopCount(1<<40) returns 0 instead of 1).
	for i := 0; i < 32; i++ {
		if x&(1<<uint(i)) != 0 {
			count++
		}
	}
	return count
}
