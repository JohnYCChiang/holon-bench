package combat

import "testing"

func TestIgnoresClientDamage(t *testing.T) {
	// Attacker is weaker than the armor, so authoritative damage is 0 even though
	// the client claims a huge hit.
	hp := Resolve(100, Attack{AttackerPower: 5, TargetArmor: 10, ClientDamage: 9999})
	if hp != 100 {
		t.Fatalf("client damage was trusted: hp = %d, want 100", hp)
	}
}

func TestAuthoritativeDamage(t *testing.T) {
	hp := Resolve(100, Attack{AttackerPower: 30, TargetArmor: 10, ClientDamage: 0})
	if hp != 80 {
		t.Fatalf("authoritative damage wrong: hp = %d, want 80", hp)
	}
}

func TestHPClampedAtZero(t *testing.T) {
	hp := Resolve(10, Attack{AttackerPower: 100, TargetArmor: 0, ClientDamage: 0})
	if hp != 0 {
		t.Fatalf("hp went negative: hp = %d, want 0", hp)
	}
}
