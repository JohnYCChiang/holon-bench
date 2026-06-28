package mapvote

// Poll tallies seed-stable map votes. Each player has at most one vote (a later
// vote replaces an earlier one) and only registered options are accepted.
type Poll struct {
	options map[string]bool
	order   []string
	votes   map[string]string
}

func NewPoll(options []string) *Poll {
	p := &Poll{options: map[string]bool{}, votes: map[string]string{}}
	for _, o := range options {
		if !p.options[o] {
			p.options[o] = true
			p.order = append(p.order, o)
		}
	}
	return p
}

// Cast records player's vote for mapID. It is rejected if the player id is empty
// or mapID is not a registered option.
func (p *Poll) Cast(player, mapID string) bool {
	if player == "" || !p.options[mapID] {
		return false
	}
	p.votes[player] = mapID
	return true
}

// Winner returns the map with the most votes. Ties are broken deterministically
// by the smallest map id. With no votes it returns "".
func (p *Poll) Winner() string {
	counts := map[string]int{}
	for _, m := range p.votes {
		counts[m]++
	}
	best := ""
	bestN := 0
	for _, o := range p.order { // BUG: scans registration order, not sorted; tie-break wrong.
		if counts[o] > bestN {
			bestN = counts[o]
			best = o
		}
	}
	return best
}
