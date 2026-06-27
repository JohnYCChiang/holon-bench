package durfmt

import "testing"

func TestFormatCarriesMinutes(t *testing.T) {
	if got := Format(3661); got != "1h1m1s" {
		t.Fatalf("Format(3661) = %q, want %q", got, "1h1m1s")
	}
}
