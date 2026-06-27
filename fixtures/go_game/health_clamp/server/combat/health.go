package combat

type Entity struct {
	HP  int
	Max int
}

// Apply applies delta (negative damages, positive heals) and clamps HP to [0, Max].
func (e *Entity) Apply(delta int) {
	e.HP += delta
}
