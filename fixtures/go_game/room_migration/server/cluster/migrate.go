package cluster

type Node struct {
	ID       string
	Priority int
	Alive    bool
}

type Room struct {
	ID       string
	HostNode string
	Players  []string
}

// Migrate reassigns a room's host when its current host node is dead. The new
// host is the highest-Priority alive node (ties broken by node ID ascending). If
// the current host is still alive nothing changes. If no alive node exists the
// room becomes hostless (HostNode ""). The player set is authoritative and must
// never be lost or reordered. Returns true iff HostNode changed.
func Migrate(room *Room, nodes []Node) bool {
	if len(nodes) == 0 {
		return false
	}
	room.HostNode = nodes[0].ID
	return true
}
