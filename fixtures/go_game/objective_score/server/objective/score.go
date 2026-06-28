package objective

// Match scores control-point ownership. Each tick, every controlled point
// grants one point to its owning team. Only registered points can be captured.
type Match struct {
	valid map[string]bool
	owner map[string]string
	score map[string]int
}

func NewMatch(points []string) *Match {
	m := &Match{valid: map[string]bool{}, owner: map[string]string{}, score: map[string]int{}}
	for _, p := range points {
		m.valid[p] = true
	}
	return m
}

// Capture gives point to team. It is rejected (state unchanged) if the point is
// not registered or the team id is empty.
func (m *Match) Capture(point, team string) bool {
	// BUG: trusts the client; captures any point for any team.
	m.owner[point] = team
	return true
}

// Tick awards one point to the owner of each controlled point.
func (m *Match) Tick() {
	for _, team := range m.owner {
		m.score[team]++
	}
}

func (m *Match) Score(team string) int { return m.score[team] }
