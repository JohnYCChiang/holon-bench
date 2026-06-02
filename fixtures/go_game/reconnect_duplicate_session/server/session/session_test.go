package session

import (
	"testing"
	"time"
)

func TestReconnectReusesExistingSession(t *testing.T) {
	now := time.Unix(1000, 0)
	store := NewStore(func() time.Time { return now })
	original := store.Create("token-1", "player-1", "lobby-1", time.Minute)

	reconnected, ok := store.Reconnect("token-1")
	if !ok {
		t.Fatal("expected reconnect to succeed")
	}
	if reconnected != original {
		t.Fatalf("expected same session pointer, got new session %#v", reconnected)
	}
	if reconnected.PlayerID != "player-1" {
		t.Fatalf("player id changed: %q", reconnected.PlayerID)
	}
	if members := store.LobbyMembers("lobby-1"); len(members) != 1 || members[0] != "player-1" {
		t.Fatalf("lobby membership duplicated: %#v", members)
	}
}

func TestReconnectRejectsExpiredSession(t *testing.T) {
	now := time.Unix(1000, 0)
	store := NewStore(func() time.Time { return now })
	store.Create("token-1", "player-1", "lobby-1", time.Second)
	now = now.Add(2 * time.Second)

	if _, ok := store.Reconnect("token-1"); ok {
		t.Fatal("expired reconnect should be rejected")
	}
}
