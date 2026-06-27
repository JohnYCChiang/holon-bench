package cdr

// Effective computes the authoritative cooldown after cooldown-reduction (CDR).
//
// Positive reduction percentages stack additively; negative entries are ignored.
// The combined CDR is capped at maxCDR, which is itself clamped to [0, 100]. The
// effective cooldown is base * (100 - cdr) / 100 using integer floor, and is
// clamped to [0, base]. clientCooldown (the client's claimed value) is ignored.
func Effective(base int, reductions []int, maxCDR int, clientCooldown int) int {
	// BUG: trusts the client's claimed cooldown and does no CDR math at all.
	return clientCooldown
}
