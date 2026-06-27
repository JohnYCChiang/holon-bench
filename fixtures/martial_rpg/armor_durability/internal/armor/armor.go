package armor

// Plate models a piece of armor. Durability and Mitigation are server-owned.
// ClientDurability is whatever the client claims and must never be trusted.
type Plate struct {
	Durability       int
	Mitigation       int
	ClientDurability int
}

// Absorb resolves an incoming hit against the plate. It returns the updated
// plate and the damage actually dealt to the wearer. The server must compute
// everything authoritatively: while the plate still has durability it reduces
// damage by Mitigation and loses one point of durability; a broken plate
// (durability 0) provides no mitigation. Durability must never go negative and
// dealt damage must never be negative.
func Absorb(p Plate, incoming int) (Plate, int) {
	p.Durability = p.ClientDurability // BUG: trusts the client's durability
	dealt := incoming - p.Mitigation  // BUG: mitigates even when broken; can be negative
	p.Durability = p.Durability - 1   // BUG: can drive durability negative
	return p, dealt
}
