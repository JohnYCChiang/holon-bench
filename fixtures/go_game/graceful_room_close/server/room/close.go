package room

type Player struct {
	ID        string
	Connected bool
	Notified  int
}

type Room struct {
	Closed  bool
	Players []Player
}

func (r *Room) Close() {
	r.Closed = true
	for i := range r.Players {
		r.Players[i].Notified++
	}
}
