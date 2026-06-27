package dodge

// DodgeState is the authoritative state of a unit that may have dodged. A dodge
// started at DodgeTick grants invulnerability for IFrames ticks: a hit landing at
// tick t is fully negated iff DodgeTick <= t < DodgeTick+IFrames.
// ClientInvulnerable is whatever the client claims and must never be trusted.
type DodgeState struct {
	HP                 int
	DodgeTick          int
	IFrames            int
	ClientInvulnerable bool
}

// ResolveHit returns the unit's new HP after a hit of `damage` at `hitTick`.
// During i-frames the hit is fully negated; otherwise damage applies and HP is
// clamped at 0. Negative damage must never heal.
func ResolveHit(s DodgeState, hitTick, damage int) int {
	if s.ClientInvulnerable { // BUG: trusts the client's invulnerability claim
		return s.HP
	}
	return s.HP - damage // BUG: ignores the i-frame window and can drive HP negative
}
