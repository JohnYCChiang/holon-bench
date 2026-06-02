package match

type Queue struct {
	players []string
}

func (q *Queue) Enqueue(player string) {
	q.players = append(q.players, player)
}

func (q *Queue) Cancel(player string) {}

func (q *Queue) Match(size int) []string {
	if len(q.players) < size {
		return nil
	}
	matched := append([]string(nil), q.players[:size]...)
	q.players = q.players[size:]
	return matched
}
