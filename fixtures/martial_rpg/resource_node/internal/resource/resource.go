package resource

// Node is a harvestable resource node. Amount is the server-owned remaining
// stock. ClientAmount is whatever the client claims it has and must never be
// trusted.
type Node struct {
	Amount       int
	ClientAmount int
}

// Harvest extracts up to `requested` units from the node. The server must
// compute the yield authoritatively: a non-positive request or a depleted node
// yields nothing, otherwise the yield is the smaller of the request and the
// remaining stock. The node's Amount is reduced by the yield and must never go
// negative. ClientAmount is never trusted. Returns the updated node and the
// units actually granted.
func Harvest(n Node, requested int) (Node, int) {
	n.Amount = n.ClientAmount   // BUG: trusts the client's stock claim
	n.Amount = n.Amount - requested // BUG: can go negative; ignores remaining stock
	return n, requested         // BUG: always grants the full request
}
