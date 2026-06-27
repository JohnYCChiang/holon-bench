package textutil

// ReverseRunes returns s with its Unicode code points in reverse order.
// It must operate on runes so multi-byte characters are not corrupted.
func ReverseRunes(s string) string {
	b := []byte(s)
	for i, j := 0, len(b)-1; i < j; i, j = i+1, j-1 {
		b[i], b[j] = b[j], b[i]
	}
	return string(b)
}
