package poise

// PoiseState is authoritative combatant poise. Poise depletes as hits land; when
// it breaks the combatant is staggered and poise is restored to MaxPoise.
type PoiseState struct {
	Poise     int
	MaxPoise  int
	Staggered bool
}

// Hit is an incoming attack. PoiseDamage is server-owned; ClientStaggered is the
// client's claim and must never be trusted.
type Hit struct {
	PoiseDamage     int
	ClientStaggered bool
}

// ApplyPoiseDamage authoritatively applies poise damage. Poise must never go
// negative; when it would reach 0 or below the combatant staggers and poise is
// restored to MaxPoise. The client's stagger claim must be ignored.
func ApplyPoiseDamage(s PoiseState, hit Hit) PoiseState {
	s.Poise -= hit.PoiseDamage        // BUG: can drive poise negative
	s.Staggered = hit.ClientStaggered // BUG: trusts the client's stagger claim
	return s
}
