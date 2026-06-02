package lobby

import "testing"

func TestJoinEnforcesCapacityAndIsIdempotent(t *testing.T) {
	l := &Lobby{Capacity: 2}
	if !l.Join("a") || !l.Join("b") {
		t.Fatal("expected first two joins to succeed")
	}
	if !l.Join("a") {
		t.Fatal("existing player rejoin should succeed")
	}
	if l.Join("c") {
		t.Fatal("new player should be rejected when lobby is full")
	}
	want := []string{"a", "b"}
	if len(l.Players) != len(want) || l.Players[0] != "a" || l.Players[1] != "b" {
		t.Fatalf("players = %#v, want %#v", l.Players, want)
	}
}
