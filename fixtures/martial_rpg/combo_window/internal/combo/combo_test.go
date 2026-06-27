package combo

import "testing"

func TestFirstHitStartsAtOne(t *testing.T) {
	s := Advance(ComboState{Count: 0, LastTick: 0, Window: 5}, Input{Tick: 10, ClientCount: 99})
	if s.Count != 1 {
		t.Fatalf("first hit count = %d, want 1", s.Count)
	}
}

func TestWithinWindowExtends(t *testing.T) {
	s := ComboState{Count: 1, LastTick: 10, Window: 5}
	s = Advance(s, Input{Tick: 13})
	if s.Count != 2 {
		t.Fatalf("count = %d, want 2", s.Count)
	}
}

func TestOutsideWindowResets(t *testing.T) {
	s := ComboState{Count: 4, LastTick: 10, Window: 5}
	s = Advance(s, Input{Tick: 20}) // gap 10 > window 5
	if s.Count != 1 {
		t.Fatalf("count = %d, want 1 after window lapse", s.Count)
	}
}
