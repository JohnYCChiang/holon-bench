package moderation

import "testing"

func TestBanExpires(t *testing.T) {
	r := NewRegistry()
	r.Ban("a", 10)
	if r.CanAct("a", 5) {
		t.Fatal("player must be barred during the ban window")
	}
	if !r.CanAct("a", 10) {
		t.Fatal("ban must expire at the until tick")
	}
}

func TestUnbannedCanAct(t *testing.T) {
	r := NewRegistry()
	if !r.CanAct("b", 0) {
		t.Fatal("never-banned player must be able to act")
	}
}
