package netcode

import "testing"

func TestPairBracketsTarget(t *testing.T) {
	b := NewBuffer(2)
	b.Add(Snapshot{Tick: 10, X: 100})
	b.Add(Snapshot{Tick: 12, X: 120})
	b.Add(Snapshot{Tick: 14, X: 140})
	lo, hi, ok := b.Pair(15) // target 13
	if !ok {
		t.Fatal("expected a bracketing pair")
	}
	if lo.Tick != 12 || hi.Tick != 14 {
		t.Fatalf("wrong bracket lo=%v hi=%v", lo, hi)
	}
}

func TestOutOfOrderAddStillOrdered(t *testing.T) {
	b := NewBuffer(0)
	b.Add(Snapshot{Tick: 30, X: 3})
	b.Add(Snapshot{Tick: 10, X: 1})
	b.Add(Snapshot{Tick: 20, X: 2})
	lo, hi, ok := b.Pair(20) // target 20 exact
	if !ok || lo.Tick != 20 || hi.Tick != 20 {
		t.Fatalf("exact target broken: lo=%v hi=%v ok=%v", lo, hi, ok)
	}
}
