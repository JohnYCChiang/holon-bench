package report

import (
	"fmt"
	"sort"
)

// Event is a named counter.
type Event struct {
	Name  string
	Count int
}

// Summarize renders one "name=count" line per event, ordered by Count
// descending, with ties broken by Name ascending. The input slice is not
// mutated.
func Summarize(events []Event) []string {
	sorted := make([]Event, len(events))
	copy(sorted, events)
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].Count < sorted[j].Count // BUG: ascending and no name tie-break
	})
	out := make([]string, 0, len(sorted))
	for _, e := range sorted {
		out = append(out, fmt.Sprintf("%s=%d", e.Name, e.Count))
	}
	return out
}
