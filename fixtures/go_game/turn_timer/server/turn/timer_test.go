package turn

import "testing"

func TestOnlyCurrentPlayerActs(t *testing.T) {
	g := NewGame([]string{"a", "b"}, 0, 10)
	if g.Act("b", 1) {
		t.Fatal("only the current player may act")
	}
	if g.Current() != "a" {
		t.Fatalf("current=%s want a (no advance on rejected act)", g.Current())
	}
}

func TestExpiredActRejected(t *testing.T) {
	g := NewGame([]string{"a", "b"}, 0, 10)
	if g.Act("a", 10) {
		t.Fatal("acting at or after the deadline must be rejected")
	}
}
