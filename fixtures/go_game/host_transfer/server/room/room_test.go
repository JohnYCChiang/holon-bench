package room

import "testing"

func TestHostTransfersToOldestConnectedPlayer(t *testing.T) {
	r := New("r1", []Player{
		{ID: "host", JoinedAt: 1, Connected: true},
		{ID: "newer", JoinedAt: 3, Connected: true},
		{ID: "oldest", JoinedAt: 2, Connected: true},
	})
	r.Leave("host")
	if r.Closed {
		t.Fatal("room should remain open")
	}
	if r.HostID != "oldest" {
		t.Fatalf("HostID = %q, want oldest", r.HostID)
	}
}

func TestHostTransferSkipsDisconnectedPlayers(t *testing.T) {
	r := New("r1", []Player{
		{ID: "host", JoinedAt: 1, Connected: true},
		{ID: "disconnected", JoinedAt: 2, Connected: false},
		{ID: "connected", JoinedAt: 3, Connected: true},
	})
	r.Leave("host")
	if r.HostID != "connected" {
		t.Fatalf("HostID = %q, want connected", r.HostID)
	}
}

func TestEmptyRoomCloses(t *testing.T) {
	r := New("r1", []Player{{ID: "solo", JoinedAt: 1, Connected: true}})
	r.Leave("solo")
	if !r.Closed {
		t.Fatal("room should close when last player leaves")
	}
	if r.HostID != "" {
		t.Fatalf("closed room should not have host, got %q", r.HostID)
	}
}
