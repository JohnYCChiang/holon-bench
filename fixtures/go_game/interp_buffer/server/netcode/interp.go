package netcode

type Snapshot struct {
	Tick int
	X    int
}

type Buffer struct {
	Delay int
	snaps []Snapshot
}

func NewBuffer(delay int) *Buffer { return &Buffer{Delay: delay} }

// Add stores a snapshot. The buffer stays ordered by Tick ascending and deduped
// by Tick (a later Add for an existing tick replaces it), regardless of the
// order snapshots arrive in.
func (b *Buffer) Add(s Snapshot) {
	b.snaps = append(b.snaps, s)
}

// Pair returns the two snapshots bracketing the render tick (now - Delay): lo is
// the latest snapshot with Tick <= target and hi is the earliest with Tick >=
// target. ok is false when the render tick falls outside the buffered range.
func (b *Buffer) Pair(now int) (lo, hi Snapshot, ok bool) {
	if len(b.snaps) < 2 {
		return Snapshot{}, Snapshot{}, false
	}
	return b.snaps[len(b.snaps)-2], b.snaps[len(b.snaps)-1], true
}
