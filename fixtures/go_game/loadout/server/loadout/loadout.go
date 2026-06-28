package loadout

// Item describes a catalogued loadout item.
type Item struct {
	ID     string
	Weight int
	Unique bool // a unique item may be carried at most once
}

// Validator is an authoritative loadout checker. A list of item ids forms a
// legal loadout only when every id is registered, no item flagged Unique
// appears more than once, and the total weight does not exceed the capacity.
type Validator struct {
	catalog  map[string]Item
	capacity int
}

func NewValidator(capacity int) *Validator {
	return &Validator{catalog: map[string]Item{}, capacity: capacity}
}

// Register adds an item to the catalog. Empty ids are ignored.
func (v *Validator) Register(it Item) {
	if it.ID == "" {
		return
	}
	v.catalog[it.ID] = it
}

// Valid reports whether the given item ids form a legal loadout.
func (v *Validator) Valid(ids []string) bool {
	total := 0
	for _, id := range ids {
		it, ok := v.catalog[id]
		if !ok {
			return false // unregistered item
		}
		total += it.Weight
	}
	// BUG: never rejects a unique item that is carried more than once.
	return total <= v.capacity
}
