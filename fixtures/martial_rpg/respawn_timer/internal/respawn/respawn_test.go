package respawn

import "testing"

func TestTimerDecrements(t *testing.T) {
	r := Tick(Respawn{Remaining: 3, Dead: true}, Input{})
	if r.Remaining != 2 || !r.Dead {
		t.Fatalf("got {%d,%v}, want {2,true}", r.Remaining, r.Dead)
	}
}

func TestReachingZeroRespawns(t *testing.T) {
	r := Tick(Respawn{Remaining: 1, Dead: true}, Input{})
	if r.Remaining != 0 || r.Dead {
		t.Fatalf("got {%d,%v}, want {0,false}", r.Remaining, r.Dead)
	}
}

func TestLivingUnitUntouched(t *testing.T) {
	r := Tick(Respawn{Remaining: 0, Dead: false}, Input{})
	if r.Remaining != 0 || r.Dead {
		t.Fatalf("got {%d,%v}, want {0,false}", r.Remaining, r.Dead)
	}
}
