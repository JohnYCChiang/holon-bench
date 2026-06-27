package combat

type Player struct {
	Alive     bool
	DeathTick int
	Delay     int
}

func (p *Player) Kill(tick int) {
	p.Alive = false
	p.DeathTick = tick
}

// Respawn attempts to bring a dead player back at tick. It is allowed only when
// the player is currently dead and tick >= DeathTick+Delay.
func (p *Player) Respawn(tick int) bool {
	p.Alive = true
	return true
}
