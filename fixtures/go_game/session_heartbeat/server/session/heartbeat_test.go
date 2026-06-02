package session

import "testing"

func TestHeartbeatExtendsDeadlineAndExpireBoundary(t *testing.T) {
	store := &Store{
		TTL: 10,
		Sessions: map[string]Session{
			"a": {ID: "a", Deadline: 10},
			"b": {ID: "b", Deadline: 5},
		},
	}
	if !store.Heartbeat("a", 8) {
		t.Fatal("heartbeat should succeed")
	}
	expired := store.Expire(18)
	if len(expired) != 1 || expired[0] != "b" {
		t.Fatalf("expired = %#v, want only b", expired)
	}
	if got := store.Sessions["a"].Deadline; got != 18 {
		t.Fatalf("deadline = %d, want 18", got)
	}
}
