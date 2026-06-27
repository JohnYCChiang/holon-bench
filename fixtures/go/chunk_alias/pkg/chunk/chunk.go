package chunk

// Chunk splits s into consecutive groups of at most size elements. Each
// returned chunk must be independent: appending to one chunk must not corrupt
// s or any other chunk.
func Chunk(s []int, size int) [][]int {
	out := [][]int{}
	if size < 1 {
		return out
	}
	for i := 0; i < len(s); i += size {
		end := i + size
		if end > len(s) {
			end = len(s)
		}
		out = append(out, s[i:end])
	}
	return out
}
