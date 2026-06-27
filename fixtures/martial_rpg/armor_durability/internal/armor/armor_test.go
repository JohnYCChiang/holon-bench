package armor

import "testing"

func TestMitigatesWhileDurable(t *testing.T) {
	p, dealt := Absorb(Plate{Durability: 5, Mitigation: 3, ClientDurability: 99}, 10)
	if dealt != 7 {
		t.Fatalf("dealt = %d, want 7", dealt)
	}
	if p.Durability != 4 {
		t.Fatalf("durability = %d, want 4", p.Durability)
	}
}

func TestBrokenArmorNoMitigation(t *testing.T) {
	p, dealt := Absorb(Plate{Durability: 0, Mitigation: 5}, 8)
	if dealt != 8 {
		t.Fatalf("broken armor mitigated: dealt = %d, want 8", dealt)
	}
	if p.Durability != 0 {
		t.Fatalf("durability went off zero: %d", p.Durability)
	}
}

func TestIgnoresClientDurability(t *testing.T) {
	p, _ := Absorb(Plate{Durability: 1, Mitigation: 2, ClientDurability: 100}, 5)
	if p.Durability != 0 {
		t.Fatalf("client durability trusted: durability = %d, want 0", p.Durability)
	}
}
