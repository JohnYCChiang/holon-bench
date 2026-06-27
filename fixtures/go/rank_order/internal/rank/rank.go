package rank

import "sort"

type Item struct {
	Name  string
	Score int
}

// Rank orders items by Score descending, breaking ties by Name ascending.
// The input slice must not be mutated.
func Rank(items []Item) []Item {
	out := make([]Item, len(items))
	copy(out, items)
	sort.SliceStable(out, func(i, j int) bool {
		return out[i].Score > out[j].Score
	})
	return out
}
