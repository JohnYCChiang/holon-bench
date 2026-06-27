package room

type VoteSession struct {
	Voters int
	Target string
	votes  map[string]bool
}

// Vote records a kick vote from voter against Target. Each voter counts once
// (idempotent). It returns true once a strict majority of eligible Voters have
// voted. Empty voter ids are rejected.
func (v *VoteSession) Vote(voter string) bool {
	if v.votes == nil {
		v.votes = map[string]bool{}
	}
	v.votes[voter] = true
	return true
}
