package bignum

import "testing"

func TestParseIDLargeNoPrecisionLoss(t *testing.T) {
	// 2^53 + 1 cannot be represented exactly as a float64.
	got, err := ParseID([]byte(`{"id":9007199254740993}`))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got != 9007199254740993 {
		t.Fatalf("ParseID = %d, want 9007199254740993", got)
	}
}

func TestParseIDSmall(t *testing.T) {
	got, err := ParseID([]byte(`{"id":42}`))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got != 42 {
		t.Fatalf("ParseID = %d, want 42", got)
	}
}
