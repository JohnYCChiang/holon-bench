package world

type Projectile struct {
	ID        string
	SpawnTick int
	TTL       int
}

type World struct {
	Projectiles []Projectile
}

// Step removes projectiles whose lifetime has ended at the given tick.
// A projectile expires when tick >= SpawnTick+TTL. Survivor order is preserved.
func (w *World) Step(tick int) {
}
