package crit

import "testing"

func TestRateBounds(t *testing.T) {
	never := NewEngine(1, 0, 2)
	always := NewEngine(1, 100, 2)
	for i := 0; i < 16; i++ {
		if _, c := never.Attack(10); c {
			t.Fatal("crit rate 0 must never crit")
		}
		if d, c := always.Attack(10); !c || d != 20 {
			t.Fatalf("crit rate 100 must always crit for 2x: dmg=%d crit=%v", d, c)
		}
	}
}

func TestStreamVaries(t *testing.T) {
	e := NewEngine(42, 50, 3)
	seenCrit, seenNormal := false, false
	for i := 0; i < 32; i++ {
		if _, c := e.Attack(10); c {
			seenCrit = true
		} else {
			seenNormal = true
		}
	}
	if !seenCrit || !seenNormal {
		t.Fatal("a 50% stream over 32 attacks must produce both crits and non-crits")
	}
}
