package spawn

type Rotator struct {
	points int
	cursor int
}

func NewRotator(points int) *Rotator { return &Rotator{points: points} }

// Assign returns a spawn-point index in [0,points) for every player. It is
// authoritative and replay-deterministic: players are processed in sorted ID
// order and assigned consecutive points starting from the rotator's cursor, so
// when len(players) <= points no two players in the same call share a point. The
// cursor then advances so successive waves rotate. The result must not depend on
// the input slice order.
func (r *Rotator) Assign(players []string) map[string]int {
	out := map[string]int{}
	for i, p := range players {
		out[p] = i % r.points
	}
	return out
}
