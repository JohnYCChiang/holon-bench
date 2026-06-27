package mana

// Pool is authoritative mana state for one unit.
type Pool struct {
	Mana  int
	Max   int
	Regen int
}

// Input is one tick's action. ClientMana is the client's claimed mana.
type Input struct {
	Spend      int
	ClientMana int
}

// Tick resolves one fixed timestep, spending then regenerating, clamped to Max.
func Tick(p Pool, in Input) Pool {
	// BUG: trusts the client's claimed mana and never clamps to [0, Max].
	p.Mana = in.ClientMana - in.Spend + p.Regen
	return p
}
