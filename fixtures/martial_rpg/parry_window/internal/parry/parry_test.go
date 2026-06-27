package parry

import "testing"

func TestPerfectParryReflects(t *testing.T) {
	out := Resolve(Hit{HP: 100, Damage: 30, ParryTick: 10, HitTick: 11, ActiveFrames: 5, PerfectFrames: 2})
	if out.HP != 100 || out.Reflected != 30 {
		t.Fatalf("got %+v, want {HP:100 Reflected:30}", out)
	}
}

func TestHitOutsideWindowApplies(t *testing.T) {
	out := Resolve(Hit{HP: 100, Damage: 30, ParryTick: 10, HitTick: 20, ActiveFrames: 5, PerfectFrames: 2})
	if out.HP != 70 || out.Reflected != 0 {
		t.Fatalf("got %+v, want {HP:70 Reflected:0}", out)
	}
}

func TestLateParryNegatesButNoReflect(t *testing.T) {
	out := Resolve(Hit{HP: 100, Damage: 30, ParryTick: 10, HitTick: 13, ActiveFrames: 5, PerfectFrames: 2})
	if out.HP != 100 || out.Reflected != 0 {
		t.Fatalf("got %+v, want {HP:100 Reflected:0}", out)
	}
}
