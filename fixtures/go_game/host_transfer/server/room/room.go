package room

type Player struct {
	ID        string
	JoinedAt  int
	Connected bool
}

type Room struct {
	ID      string
	HostID  string
	Closed  bool
	Players []Player
}

func New(id string, players []Player) *Room {
	r := &Room{ID: id, Players: append([]Player(nil), players...)}
	for _, p := range r.Players {
		if p.Connected {
			r.HostID = p.ID
			break
		}
	}
	return r
}

func (r *Room) Leave(playerID string) {
	remaining := r.Players[:0]
	for _, p := range r.Players {
		if p.ID != playerID {
			remaining = append(remaining, p)
		}
	}
	r.Players = remaining
	if len(r.Players) == 0 {
		r.Closed = true
		r.HostID = ""
		return
	}
	if r.HostID == playerID {
		r.HostID = ""
	}
}
