package moderation

// Registry is the authoritative ban list. A banned player cannot act until the
// ban expires. Bans are keyed by player id with an expiry tick.
type Registry struct {
	bans map[string]int64
}

func NewRegistry() *Registry { return &Registry{bans: map[string]int64{}} }

// Ban bars id from acting until the given tick. Empty ids are ignored.
func (r *Registry) Ban(id string, until int64) {
	if id == "" {
		return
	}
	r.bans[id] = until
}

// CanAct reports whether id may act at tick now. A ban expires exactly at its
// until tick: at now >= until the player may act again.
func (r *Registry) CanAct(id string, now int64) bool {
	_, banned := r.bans[id]
	return !banned // BUG: ignores expiry; a banned player is barred forever.
}
