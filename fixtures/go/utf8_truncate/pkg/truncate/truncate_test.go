package truncate

import (
	"testing"
	"unicode/utf8"
)

func TestTruncateDoesNotSplitRune(t *testing.T) {
	// "aé" is bytes: 'a' (1 byte) + 'é' (0xC3 0xA9, 2 bytes) = 3 bytes.
	got := Truncate("aé", 2)
	if !utf8.ValidString(got) {
		t.Fatalf("Truncate produced invalid UTF-8: %q", got)
	}
	if got != "a" {
		t.Fatalf("Truncate(\"aé\", 2) = %q, want %q", got, "a")
	}
}

func TestTruncateFits(t *testing.T) {
	if got := Truncate("hello", 10); got != "hello" {
		t.Fatalf("Truncate = %q, want %q", got, "hello")
	}
}
