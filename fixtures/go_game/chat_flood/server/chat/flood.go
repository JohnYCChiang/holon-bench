package chat

type Filter struct {
	Max    int
	Window int64
	hist   map[string][]int64
}

func NewFilter(max int, window int64) *Filter {
	return &Filter{Max: max, Window: window, hist: map[string][]int64{}}
}

// Allow reports whether a message from player at time now is accepted. At most
// Max messages are accepted within any sliding window of length Window (a prior
// message counts only while its timestamp > now-Window). Accepted messages are
// recorded; dropped ones are not. The clock is non-decreasing per player.
func (f *Filter) Allow(player string, now int64) bool {
	if f.hist == nil {
		f.hist = map[string][]int64{}
	}
	f.hist[player] = append(f.hist[player], now)
	return len(f.hist[player]) <= f.Max
}
