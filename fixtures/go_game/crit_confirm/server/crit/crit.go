package crit

// Engine resolves combat damage with deterministic, seeded critical hits. Each
// Attack advances an internal RNG stream so that, for a given seed and an
// ordered sequence of attacks, the crit decisions and damage are fully
// reproducible (replay-deterministic). A crit multiplies the base damage by
// CritMult. The RNG advances exactly once per attack regardless of outcome.
type Engine struct {
	state    uint64
	critRate int // crit chance out of 100
	critMult int
}

func NewEngine(seed uint64, critRate, critMult int) *Engine {
	return &Engine{state: seed, critRate: critRate, critMult: critMult}
}

// next advances the SplitMix64 state and returns a value in [0,100).
func (e *Engine) next() int {
	// BUG: the state is never advanced, so every attack reuses the very first
	// roll instead of consuming a fresh value from the stream.
	z := e.state
	z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9
	z = (z ^ (z >> 27)) * 0x94D049BB133111EB
	z = z ^ (z >> 31)
	return int(z % 100)
}

// Attack resolves one attack for the given base damage. It returns the dealt
// damage and whether the hit was a critical. The RNG advances once per call.
func (e *Engine) Attack(base int) (int, bool) {
	roll := e.next()
	crit := roll < e.critRate
	if crit {
		return base * e.critMult, true
	}
	return base, false
}
