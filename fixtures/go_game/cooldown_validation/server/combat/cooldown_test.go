package combat

import "testing"

func TestCooldownIsEnforcedPerPlayer(t *testing.T) {
	v := &Validator{Cooldown: 3}
	if got := v.Apply("a", 10); !got.Accepted || got.Rejected {
		t.Fatalf("first action = %#v, want accepted", got)
	}
	if got := v.Apply("a", 12); got.Accepted || !got.Rejected {
		t.Fatalf("cooldown action = %#v, want rejected", got)
	}
	if got := v.Apply("b", 12); !got.Accepted {
		t.Fatalf("other player should be independent: %#v", got)
	}
	if got := v.Apply("a", 13); !got.Accepted || got.Rejected {
		t.Fatalf("after cooldown = %#v, want accepted", got)
	}
}
