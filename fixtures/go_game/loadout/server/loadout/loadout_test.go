package loadout

import "testing"

func setup() *Validator {
	v := NewValidator(10)
	v.Register(Item{ID: "rifle", Weight: 6, Unique: true})
	v.Register(Item{ID: "ammo", Weight: 2, Unique: false})
	v.Register(Item{ID: "knife", Weight: 3, Unique: true})
	return v
}

func TestUniqueDuplicateRejected(t *testing.T) {
	v := setup()
	// knife is unique and two knives weigh 6 (within the capacity of 10), so
	// only the uniqueness rule can reject this loadout.
	if v.Valid([]string{"knife", "knife"}) {
		t.Fatal("a unique item carried twice must be rejected")
	}
}

func TestLegalLoadoutAccepted(t *testing.T) {
	v := setup()
	if !v.Valid([]string{"rifle", "ammo", "ammo"}) {
		t.Fatal("rifle + two ammo (weight 10) must be a legal loadout")
	}
}
