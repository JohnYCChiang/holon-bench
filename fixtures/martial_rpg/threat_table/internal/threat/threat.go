package threat

// Unit is one combatant on the authoritative threat table.
type Unit struct {
	ID     int
	Threat int
}

// Table is the server's view of current threat.
type Table struct {
	Units []Unit
}

// Input is the client's request. ClientTargetID is the client's claimed target.
type Input struct {
	ClientTargetID int
}

// Target returns the ID of the highest-threat unit; ties broken by lower ID.
func Target(t Table, in Input) int {
	// BUG: trusts the client's claimed target instead of the threat table.
	return in.ClientTargetID
}
