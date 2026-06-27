package combat

// Attack is a resolution request. AttackerPower and TargetArmor are
// server-owned stats. ClientDamage is whatever the client claims and must never
// be trusted by the authoritative server.
type Attack struct {
	AttackerPower int
	TargetArmor   int
	ClientDamage  int
}

// Resolve returns the target's new HP after the attack. The server must compute
// damage authoritatively from its own stats (power minus armor, floored at 0)
// and must never let HP go negative.
func Resolve(targetHP int, atk Attack) int {
	return targetHP - atk.ClientDamage // BUG: trusts client; can drive HP negative
}
