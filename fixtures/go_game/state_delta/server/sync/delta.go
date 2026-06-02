package sync

type Entity struct {
	X int
	Y int
}

type Delta struct {
	Changed map[string]Entity
	Removed []string
}

func BuildDelta(prev, next map[string]Entity) Delta {
	return Delta{Changed: next, Removed: nil}
}
