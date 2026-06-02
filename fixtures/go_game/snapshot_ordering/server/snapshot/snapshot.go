package snapshot

type Player struct {
	ID     string
	Joined int
}

type Entity struct {
	ID string
	X  int
}

type Room struct {
	Players  map[string]Player
	Entities map[string]Entity
}

func Snapshot(room Room) []string {
	out := []string{}
	for id := range room.Players {
		out = append(out, "p:"+id)
	}
	for id := range room.Entities {
		out = append(out, "e:"+id)
	}
	return out
}
