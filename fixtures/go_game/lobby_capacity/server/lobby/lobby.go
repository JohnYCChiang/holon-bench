package lobby

type Lobby struct {
	Capacity int
	Players []string
}

func (l *Lobby) Join(player string) bool {
	l.Players = append(l.Players, player)
	return true
}
