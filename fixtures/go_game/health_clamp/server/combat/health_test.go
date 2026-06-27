package combat

import "testing"

func TestApplyClampsToBounds(t *testing.T) {
	e := &Entity{HP: 10, Max: 100}
	e.Apply(-25)
	if e.HP != 0 {
		t.Fatalf("HP = %d, want 0 (clamped)", e.HP)
	}
	e.Apply(500)
	if e.HP != 100 {
		t.Fatalf("HP = %d, want 100 (clamped to Max)", e.HP)
	}
}
