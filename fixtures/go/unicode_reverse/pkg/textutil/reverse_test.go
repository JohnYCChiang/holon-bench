package textutil

import (
	"testing"
	"unicode/utf8"
)

func TestReverseRunesASCII(t *testing.T) {
	if got := ReverseRunes("abc"); got != "cba" {
		t.Fatalf("ReverseRunes(abc) = %q, want cba", got)
	}
}

func TestReverseRunesMultibyte(t *testing.T) {
	got := ReverseRunes("héllo")
	if got != "olléh" {
		t.Fatalf("ReverseRunes(héllo) = %q, want olléh", got)
	}
	if !utf8.ValidString(got) {
		t.Fatalf("result is not valid UTF-8: %q", got)
	}
}
