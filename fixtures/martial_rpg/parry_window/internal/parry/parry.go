package parry

// Hit describes an incoming attack against a defender who may have started a
// parry. ParryTick is when the defender began the parry; HitTick is when the
// attack lands. ClientParried is the client's claim that it parried.
type Hit struct {
	HP            int
	Damage        int
	ParryTick     int
	HitTick       int
	ActiveFrames  int
	PerfectFrames int
	ClientParried bool
}

// Result is the authoritative outcome: the defender's new HP and any damage
// reflected back at the attacker.
type Result struct {
	HP        int
	Reflected int
}

// Resolve computes the authoritative result of an incoming hit.
//
// A parry succeeds only when the hit lands within the active window
// [ParryTick, ParryTick+ActiveFrames). A successful parry negates all damage,
// and if it landed within the tighter perfect window (HitTick-ParryTick <
// PerfectFrames) the damage is reflected. Otherwise the (non-negative) damage
// applies and HP is clamped at 0. ClientParried is never trusted.
func Resolve(h Hit) Result {
	// BUG: trusts the client's parry claim and applies raw damage that can
	// drive HP negative.
	if h.ClientParried {
		return Result{HP: h.HP, Reflected: h.Damage}
	}
	return Result{HP: h.HP - h.Damage}
}
