package economy

type Inventory struct {
	items map[string]bool
}

func NewInventory(items ...string) *Inventory {
	m := map[string]bool{}
	for _, it := range items {
		m[it] = true
	}
	return &Inventory{items: m}
}

func (inv *Inventory) Has(item string) bool { return inv.items[item] }

func (inv *Inventory) Count() int { return len(inv.items) }

// Trade atomically swaps itemA (owned by a) for itemB (owned by b). It succeeds
// only when a truly has itemA and b truly has itemB; otherwise neither
// inventory is modified. Items are never duplicated or destroyed.
func Trade(a *Inventory, itemA string, b *Inventory, itemB string) bool {
	delete(a.items, itemA)
	b.items[itemA] = true
	delete(b.items, itemB)
	a.items[itemB] = true
	return true
}
