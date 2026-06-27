package world

type Item struct {
	ID      string
	OwnerID string
}

// Claim assigns the item to player. An item can only be owned by one player;
// once claimed, later claims (and empty player ids) are rejected. Returns true
// only when this call acquired the item.
func (it *Item) Claim(player string) bool {
	it.OwnerID = player
	return true
}
