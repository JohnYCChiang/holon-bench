package rank

type Entry struct {
	ID    string
	Score int
}

type Board struct {
	Cap     int
	entries []Entry
}

func NewBoard(cap int) *Board { return &Board{Cap: cap} }

// Update records player id's score and returns the current ranking as a fresh
// copy. A player appears at most once (a new score replaces the old one). The
// ranking is sorted by Score descending, ties broken by ID ascending, and is
// truncated to Cap entries. The returned slice must be independent of internal
// state so callers cannot corrupt the board.
func (b *Board) Update(id string, score int) []Entry {
	b.entries = append(b.entries, Entry{ID: id, Score: score})
	return b.entries
}
