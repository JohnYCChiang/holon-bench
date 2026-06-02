package room

import "testing"

func TestCloseIsIdempotentAndNotifiesConnectedOnce(t *testing.T) {
	r := &Room{Players: []Player{
		{ID: "a", Connected: true},
		{ID: "b", Connected: false},
		{ID: "c", Connected: true},
	}}
	r.Close()
	r.Close()
	if !r.Closed {
		t.Fatal("room should be closed")
	}
	if r.Players[0].Notified != 1 || r.Players[1].Notified != 0 || r.Players[2].Notified != 1 {
		t.Fatalf("players = %#v, want connected players notified once", r.Players)
	}
}
