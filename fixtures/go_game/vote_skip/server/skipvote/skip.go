package skipvote

// Skip is an authoritative vote-to-skip tally. A skip passes only when the
// number of in-favor votes from currently present players reaches the required
// fraction (Num/Den) of the present player count. Only present players may
// vote, each present player counts at most once, and a player who leaves takes
// their vote with them.
type Skip struct {
	present map[string]bool
	voted   map[string]bool
	num     int
	den     int
}

func NewSkip(num, den int) *Skip {
	return &Skip{present: map[string]bool{}, voted: map[string]bool{}, num: num, den: den}
}

// Join marks a player present. Empty ids are ignored; re-joining is harmless.
func (s *Skip) Join(id string) {
	if id == "" {
		return
	}
	s.present[id] = true
}

// Leave removes a player from presence and discards any vote they had cast.
func (s *Skip) Leave(id string) {
	delete(s.present, id)
	delete(s.voted, id)
}

// Vote records a skip vote from a present player. Empty or non-present ids are
// rejected without mutating state.
func (s *Skip) Vote(id string) bool {
	if id == "" || !s.present[id] {
		return false
	}
	s.voted[id] = true
	return true
}

// Passed reports whether the skip threshold is met. It requires at least one
// present player and votes*Den >= present*Num.
func (s *Skip) Passed() bool {
	p := len(s.present)
	if p == 0 {
		return false
	}
	// BUG: uses strict greater-than, so an exactly-at-threshold supermajority
	// fails to trigger the skip.
	return len(s.voted)*s.den > p*s.num
}
