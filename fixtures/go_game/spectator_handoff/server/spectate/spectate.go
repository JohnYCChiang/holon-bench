package spectate

// Arena tracks live players in join order and the spectators that follow them.
// When a followed player leaves, that player's spectators are handed off to the
// oldest remaining live player; if no players remain they become idle (target
// ""). The handoff is authoritative and order-independent.
type Arena struct {
	players []string          // live players in join order
	live    map[string]bool   // membership set
	target  map[string]string // spectator id -> followed player id ("" = idle)
}

func NewArena() *Arena {
	return &Arena{live: map[string]bool{}, target: map[string]string{}}
}

// AddPlayer registers a live player in join order. Empty or duplicate ids are
// ignored.
func (a *Arena) AddPlayer(id string) {
	if id == "" || a.live[id] {
		return
	}
	a.live[id] = true
	a.players = append(a.players, id)
}

// Spectate attaches spectator sid to live player pid. It is rejected when sid
// is empty or pid is not a live player.
func (a *Arena) Spectate(sid, pid string) bool {
	if sid == "" || !a.live[pid] {
		return false
	}
	a.target[sid] = pid
	return true
}

// Target returns the player a spectator currently follows ("" = idle).
func (a *Arena) Target(sid string) string { return a.target[sid] }

// Leave removes a live player and hands off its spectators to the oldest
// remaining live player, or makes them idle when none remain.
func (a *Arena) Leave(pid string) {
	if !a.live[pid] {
		return
	}
	delete(a.live, pid)
	for i, p := range a.players {
		if p == pid {
			a.players = append(a.players[:i], a.players[i+1:]...)
			break
		}
	}
	// BUG: spectators of the departed player are never reassigned, so they keep
	// following a player who has already left the arena.
}
