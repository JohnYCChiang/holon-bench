package cluster

import (
	"reflect"
	"testing"
)

func TestMigrateOnHostDeath(t *testing.T) {
	room := &Room{ID: "r1", HostNode: "n1", Players: []string{"p1", "p2", "p3"}}
	nodes := []Node{
		{ID: "n1", Priority: 5, Alive: false},
		{ID: "n2", Priority: 2, Alive: true},
		{ID: "n3", Priority: 9, Alive: true},
	}
	if !Migrate(room, nodes) {
		t.Fatal("expected migration")
	}
	if room.HostNode != "n3" {
		t.Fatalf("host=%s want n3 (highest priority alive)", room.HostNode)
	}
	if !reflect.DeepEqual(room.Players, []string{"p1", "p2", "p3"}) {
		t.Fatalf("players changed: %v", room.Players)
	}
}

func TestNoMigrateWhenHostAlive(t *testing.T) {
	room := &Room{ID: "r1", HostNode: "n1", Players: []string{"p1"}}
	nodes := []Node{{ID: "n1", Priority: 1, Alive: true}, {ID: "n2", Priority: 9, Alive: true}}
	if Migrate(room, nodes) {
		t.Fatal("must not migrate when host alive")
	}
	if room.HostNode != "n1" {
		t.Fatalf("host changed to %s", room.HostNode)
	}
}
