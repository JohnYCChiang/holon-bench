package luhn

// Valid reports whether number (a string of decimal digits) passes the Luhn
// checksum. An empty string or any non-digit character makes it invalid.
func Valid(number string) bool {
	if len(number) == 0 {
		return false
	}
	sum := 0
	double := false
	for i := len(number) - 1; i >= 0; i-- {
		c := number[i]
		if c < '0' || c > '9' {
			return false
		}
		d := int(c - '0')
		if double {
			d *= 2
			// BUG: a doubled digit greater than 9 must have 9 subtracted
			// (equivalently, its digits summed). That adjustment is missing.
		}
		sum += d
		double = !double
	}
	return sum%10 == 0
}
