package board

import "sort"

type Player struct {
	Name  string
	Tier  string
	Score int
}

// Rank orders players by Tier ascending, then by Score descending, then by
// Name ascending. The ordering must be deterministic and must not mutate the
// input slice.
func Rank(players []Player) []Player {
	out := make([]Player, len(players))
	copy(out, players)
	sort.SliceStable(out, func(i, j int) bool {
		return out[i].Score > out[j].Score
	})
	return out
}
