package replay

import "testing"

func TestChecksumIsDeterministicForSemanticReplay(t *testing.T) {
	a := []Event{
		{Tick: 2, Player: "b", Action: "fire"},
		{Tick: 1, Player: "a", Action: "join"},
	}
	b := []Event{
		{Tick: 1, Player: "a", Action: "join"},
		{Tick: 2, Player: "b", Action: "fire"},
	}
	if Checksum(a) != Checksum(b) {
		t.Fatal("same semantic replay should produce same checksum")
	}
	if Checksum(a) == Checksum([]Event{{Tick: 1, Player: "a", Action: "move"}}) {
		t.Fatal("different replay should produce different checksum")
	}
}
