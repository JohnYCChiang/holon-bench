package luhn

import "testing"

func TestDoubledDigitOverNineIsAdjusted(t *testing.T) {
	// "59": doubling the 5 gives 10, which must contribute 1 (10-9), not 10.
	if !Valid("59") {
		t.Fatalf("Valid(\"59\") = false, want true")
	}
}
