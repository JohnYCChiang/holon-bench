package world

import "testing"

func TestStepRemovesExpired(t *testing.T) {
	w := &World{Projectiles: []Projectile{
		{ID: "a", SpawnTick: 0, TTL: 5},
		{ID: "b", SpawnTick: 2, TTL: 10},
		{ID: "c", SpawnTick: 0, TTL: 3},
	}}
	w.Step(5)
	if len(w.Projectiles) != 1 || w.Projectiles[0].ID != "b" {
		t.Fatalf("survivors=%#v want [b]", w.Projectiles)
	}
}
