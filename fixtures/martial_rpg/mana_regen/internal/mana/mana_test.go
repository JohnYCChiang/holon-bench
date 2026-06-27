package mana

import "testing"

func TestRegenClampsAtMax(t *testing.T) {
	out := Tick(Pool{Mana: 90, Max: 100, Regen: 20}, Input{})
	if out.Mana != 100 {
		t.Fatalf("mana = %d, want 100", out.Mana)
	}
}

func TestSpendThenRegen(t *testing.T) {
	out := Tick(Pool{Mana: 50, Max: 100, Regen: 10}, Input{Spend: 30})
	if out.Mana != 30 {
		t.Fatalf("mana = %d, want 30", out.Mana)
	}
}

func TestOverspendRejected(t *testing.T) {
	out := Tick(Pool{Mana: 10, Max: 100, Regen: 5}, Input{Spend: 50})
	if out.Mana != 15 {
		t.Fatalf("mana = %d, want 15 (spend rejected, regen applied)", out.Mana)
	}
}
