package respawn

// Respawn is authoritative respawn state for one unit.
type Respawn struct {
	Remaining int
	Dead      bool
}

// Input is one tick. ClientReady is the client's claimed readiness.
type Input struct {
	ClientReady bool
}

// Tick advances one fixed timestep, counting the timer down toward respawn.
func Tick(r Respawn, in Input) Respawn {
	// BUG: trusts the client's readiness flag and underflows the timer.
	if in.ClientReady {
		r.Dead = false
	}
	r.Remaining--
	return r
}
