package loot

type Roller struct {
	state uint64
}

func NewRoller(seed uint64) *Roller {
	return &Roller{state: seed}
}

type LootDrop struct {
	Player string
	Index  int
}

// Next returns the next pseudo-random value in [0, n). It MUST advance internal
// state so successive calls differ and the whole sequence is reproducible from
// the seed alone.
func (r *Roller) Next(n int) int {
	if n <= 0 {
		return 0
	}
	return int(r.state % uint64(n))
}

// RollLoot deterministically assigns a loot index in [0, tables) to each player.
// The result MUST be identical for the same player set regardless of map
// iteration order: players are processed in sorted id order, and the output is
// sorted by player id.
func RollLoot(seed uint64, players map[string]int, tables int) []LootDrop {
	r := NewRoller(seed)
	out := make([]LootDrop, 0, len(players))
	for id := range players {
		out = append(out, LootDrop{Player: id, Index: r.Next(tables)})
	}
	return out
}
