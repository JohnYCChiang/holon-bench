package registry

// Set is an insertion-ordered set of strings. Add is idempotent: adding a value
// that is already present is a no-op. Items returns each distinct value once, in
// first-insertion order.
type Set struct {
	items []string
}

// New returns an empty Set.
func New() *Set {
	return &Set{}
}

// Add inserts v if it is not already present.
func (s *Set) Add(v string) {
	s.items = append(s.items, v) // BUG: not idempotent, allows duplicates
}

// Items returns the distinct values in first-insertion order.
func (s *Set) Items() []string {
	out := make([]string, len(s.items))
	copy(out, s.items)
	return out
}
