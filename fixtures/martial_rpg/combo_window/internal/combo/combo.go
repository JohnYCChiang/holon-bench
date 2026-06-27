package combo

// ComboState is authoritative combo progression for one fighter.
type ComboState struct {
	Count    int
	LastTick int
	Window   int
}

// Input registers a hit landing at Tick. ClientCount is the client's claimed
// combo total and must never be trusted.
type Input struct {
	Tick        int
	ClientCount int
}

// Advance registers a hit. The combo count increases by 1 only when the hit
// lands strictly after LastTick and within Window ticks of it; otherwise the
// chain resets to 1. The server computes Count itself.
func Advance(s ComboState, in Input) ComboState {
	s.Count = in.ClientCount // BUG: trusts the client's combo count
	s.LastTick = in.Tick
	return s
}
