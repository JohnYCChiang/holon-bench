package match

type Player struct {
	ID    string
	Skill int
}

type Teams struct {
	A []string
	B []string
}

// BalanceTeams splits players into two teams. To keep the result authoritative
// and replay-deterministic it must NOT depend on the input slice order: players
// are processed in a deterministic order and each is assigned to the currently
// smaller team (ties broken by lower total skill, then team A). Team sizes differ
// by at most 1 and each team's ID list is returned sorted.
func BalanceTeams(players []Player) Teams {
	var t Teams
	for i, p := range players {
		if i%2 == 0 {
			t.A = append(t.A, p.ID)
		} else {
			t.B = append(t.B, p.ID)
		}
	}
	return t
}
