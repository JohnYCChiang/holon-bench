package spawn

import "testing"

func TestDamageBlockedDuringProtection(t *testing.T) {
	p := &Player{HP: 100, SpawnTick: 10, Protect: 5}
	if p.Damage(12, 30) {
		t.Fatal("damage during protection should be blocked")
	}
	if p.HP != 100 {
		t.Fatalf("HP = %d, want 100", p.HP)
	}
	if !p.Damage(15, 30) {
		t.Fatal("damage after protection should apply")
	}
	if p.HP != 70 {
		t.Fatalf("HP = %d, want 70", p.HP)
	}
}
