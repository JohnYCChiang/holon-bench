package loot

// Entry is one weighted loot-table row.
type Entry struct {
	ID     int
	Weight int
}

// Table is the authoritative weighted loot table.
type Table struct {
	Entries []Entry
}

// Roll selects an entry's ID using the provided roll value, honoring weights.
func Roll(t Table, roll uint64) int {
	// BUG: ignores weights entirely, indexes by raw roll, and can return
	// invalid (non-positive weight) entries; also depends on slice order.
	if len(t.Entries) == 0 {
		return -1
	}
	idx := int(roll) % len(t.Entries)
	return t.Entries[idx].ID
}
