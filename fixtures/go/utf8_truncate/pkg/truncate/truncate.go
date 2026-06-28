package truncate

// Truncate returns the longest prefix of s whose UTF-8 byte length does not
// exceed max, without splitting a multi-byte rune. The result is always valid
// UTF-8. A max of zero or less yields the empty string.
func Truncate(s string, max int) string {
	if max <= 0 {
		return ""
	}
	if len(s) <= max {
		return s
	}
	return s[:max]
}
