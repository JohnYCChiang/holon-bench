package retarget

// Unit is one entry in the threat table. Alive is false for units that have
// already died; deadID (passed to Retarget) is the unit that died this tick.
type Unit struct {
	ID     int
	Threat int
	Alive  bool
}

// Retarget picks the authoritative aggro target after a death.
//
// A unit is targetable only if it is Alive and is not the unit that just died
// (deadID). Among targetable units it returns the one with the highest Threat,
// breaking ties by the lowest ID. It returns -1 when no unit is targetable. The
// input slice is never mutated and the result is independent of slice order.
func Retarget(units []Unit, deadID int) int {
	// BUG: ignores the death and the Alive flag and just returns the first
	// listed unit, trusting submission order.
	if len(units) == 0 {
		return -1
	}
	return units[0].ID
}
