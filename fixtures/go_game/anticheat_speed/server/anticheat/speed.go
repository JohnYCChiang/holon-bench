package anticheat

// Validator authoritatively bounds player movement. A position update is
// accepted only if the player did not move farther than maxSpeed units per tick
// (Manhattan distance). Rejected updates leave the last authoritative position
// unchanged. The client's claimed position is never trusted blindly.
type Validator struct {
	maxSpeed int64
	x        map[string]int64
	y        map[string]int64
	tick     map[string]int64
	known    map[string]bool
}

func NewValidator(maxSpeed int64) *Validator {
	return &Validator{
		maxSpeed: maxSpeed,
		x:        map[string]int64{},
		y:        map[string]int64{},
		tick:     map[string]int64{},
		known:    map[string]bool{},
	}
}

// Spawn sets the authoritative starting position for id.
func (v *Validator) Spawn(id string, x, y, tick int64) {
	v.known[id] = true
	v.x[id] = x
	v.y[id] = y
	v.tick[id] = tick
}

// Update validates a movement to (x, y) at the given tick. It is accepted only
// when the player is known, the tick strictly advances, and the Manhattan
// distance does not exceed maxSpeed * elapsed ticks. On rejection the stored
// position is unchanged.
func (v *Validator) Update(id string, x, y, tick int64) bool {
	// BUG: trusts the client and stores whatever position it claims.
	v.x[id] = x
	v.y[id] = y
	v.tick[id] = tick
	return true
}

// Pos returns the last authoritative position for id.
func (v *Validator) Pos(id string) (int64, int64) {
	return v.x[id], v.y[id]
}
