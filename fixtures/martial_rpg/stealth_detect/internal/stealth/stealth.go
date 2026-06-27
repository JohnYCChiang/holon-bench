package stealth

// Probe is a detection query. Observer/Target coordinates and Radius are
// server-owned. ClientDetected is whatever the client claims and must never be
// trusted by the authoritative server.
type Probe struct {
	ObserverX      int
	ObserverY      int
	TargetX        int
	TargetY        int
	Radius         int
	ClientDetected bool
}

// Detect reports whether the observer detects the target. The server must
// compute this authoritatively from the squared Euclidean distance: the target
// is detected iff it lies within (inclusive of) Radius of the observer. A
// negative Radius detects nothing. ClientDetected is never trusted.
func Detect(p Probe) bool {
	return p.ClientDetected // BUG: trusts the client's detection claim
}
