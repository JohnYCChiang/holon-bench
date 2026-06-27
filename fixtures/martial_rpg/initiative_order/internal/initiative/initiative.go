package initiative

import "sort"

// Combatant is an entrant with a server-owned Speed and unique ID.
type Combatant struct {
	ID    int
	Speed int
}

// Order returns combatants in authoritative turn order: higher Speed first,
// ties broken by lower ID. The result must be deterministic and independent of
// submission order, and the caller's slice must not be mutated.
func Order(cs []Combatant) []Combatant {
	// BUG: sorts only by Speed, so ties keep submission order (non-deterministic
	// across equivalent inputs), and it sorts the caller's slice in place.
	sort.SliceStable(cs, func(i, j int) bool {
		return cs[i].Speed > cs[j].Speed
	})
	return cs
}
