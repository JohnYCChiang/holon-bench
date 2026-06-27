package semver

import "testing"

func TestCompareMultiDigitField(t *testing.T) {
	got, err := Compare("1.10.0", "1.9.0")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got != 1 {
		t.Fatalf("Compare(1.10.0, 1.9.0) = %d, want 1", got)
	}
}
