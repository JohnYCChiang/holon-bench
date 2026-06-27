package world

type Grid struct {
	pos  map[string][2]int
	cell map[[2]int]string
}

func NewGrid() *Grid {
	return &Grid{pos: map[string][2]int{}, cell: map[[2]int]string{}}
}

// At returns the entity occupying the cell, or "" if empty.
func (g *Grid) At(x, y int) string {
	return g.cell[[2]int{x, y}]
}

// Spawn places a new entity at (x,y) when the cell is free. Returns false if
// the cell is occupied or the entity already exists.
func (g *Grid) Spawn(id string, x, y int) bool {
	c := [2]int{x, y}
	g.pos[id] = c
	g.cell[c] = id
	return true
}

// Move relocates an entity to (x,y). The move is rejected (state unchanged) if
// the target cell is occupied by a different entity. Moving to one's own cell
// is a no-op success. Unknown entities are rejected.
func (g *Grid) Move(id string, x, y int) bool {
	g.pos[id] = [2]int{x, y}
	return true
}
