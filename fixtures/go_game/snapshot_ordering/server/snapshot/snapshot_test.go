package snapshot

import "testing"

func TestSnapshotOrderingIsDeterministic(t *testing.T) {
	room := Room{
		Players: map[string]Player{
			"later": {ID: "later", Joined: 2},
			"first": {ID: "first", Joined: 1},
		},
		Entities: map[string]Entity{
			"z": {ID: "z", X: 9},
			"a": {ID: "a", X: 1},
		},
	}
	got := Snapshot(room)
	want := []string{"p:first", "p:later", "e:a", "e:z"}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("snapshot = %#v, want %#v", got, want)
		}
	}
}
