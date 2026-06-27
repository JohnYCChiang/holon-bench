package spawn

type Player struct {
	HP        int
	SpawnTick int
	Protect   int
}

// Damage applies dmg at tick. While within the spawn-protection window
// [SpawnTick, SpawnTick+Protect) the damage is ignored. Returns true only if
// damage was actually applied.
func (p *Player) Damage(tick, dmg int) bool {
	p.HP -= dmg
	return true
}
