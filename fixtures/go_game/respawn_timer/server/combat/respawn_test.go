package combat

import "testing"

func TestRespawnRespectsDelay(t *testing.T) {
	p := &Player{Alive: true, Delay: 10}
	p.Kill(100)
	if p.Respawn(105) {
		t.Fatal("too early")
	}
	if p.Alive {
		t.Fatal("should still be dead")
	}
	if !p.Respawn(110) {
		t.Fatal("respawn allowed at death+delay")
	}
	if !p.Alive {
		t.Fatal("should be alive")
	}
}
