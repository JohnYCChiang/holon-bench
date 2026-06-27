package hitstop

// State is the authoritative hitstop (freeze-frame) state for one entity.
type State struct {
	Frozen int
	Max    int
}

// Input is one frame. A HitFreeze > 0 means a hit landed this frame and adds
// freeze frames. ClientFrozen is the client's claimed frozen counter.
type Input struct {
	HitFreeze    int
	ClientFrozen int
}

// Apply advances the hitstop state by one frame.
//
// When a hit lands (HitFreeze > 0) the freeze counter accumulates, clamped to
// Max. Otherwise the counter ticks down by one, never below 0. A negative Max
// is treated as 0. ClientFrozen is never trusted.
func Apply(s State, in Input) State {
	// BUG: trusts the client's frozen counter and never clamps to [0, Max].
	s.Frozen = in.ClientFrozen + in.HitFreeze
	return s
}
