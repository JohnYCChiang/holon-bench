package session

import (
	"testing"
	"time"
)

func TestHiddenRepeatedReconnectsRemainIdempotent(t *testing.T) {
	now := time.Unix(1000, 0)
	store := NewStore(func() time.Time { return now })
	original := store.Create("token-1", "player-1", "lobby-1", time.Minute)

	for i := 0; i < 5; i++ {
		reconnected, ok := store.Reconnect("token-1")
		if !ok {
			t.Fatalf("reconnect %d unexpectedly failed", i)
		}
		if reconnected != original {
			t.Fatalf("reconnect %d created a new session pointer", i)
		}
	}

	members := store.LobbyMembers("lobby-1")
	if len(members) != 1 || members[0] != "player-1" {
		t.Fatalf("repeated reconnects duplicated lobby membership: %#v", members)
	}
}

func TestHiddenRejectedReconnectDoesNotMutateLobby(t *testing.T) {
	now := time.Unix(1000, 0)
	store := NewStore(func() time.Time { return now })
	store.Create("token-1", "player-1", "lobby-1", time.Second)

	if _, ok := store.Reconnect("missing-token"); ok {
		t.Fatal("missing token reconnect should fail")
	}
	now = now.Add(2 * time.Second)
	if _, ok := store.Reconnect("token-1"); ok {
		t.Fatal("expired token reconnect should fail")
	}

	members := store.LobbyMembers("lobby-1")
	if len(members) != 1 || members[0] != "player-1" {
		t.Fatalf("failed reconnect mutated lobby membership: %#v", members)
	}
	if members := store.LobbyMembers("missing-lobby"); len(members) != 0 {
		t.Fatalf("missing reconnect created lobby membership: %#v", members)
	}
}
