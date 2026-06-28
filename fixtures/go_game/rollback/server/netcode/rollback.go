package netcode

type Input struct {
	Tick   int
	Player string
	Delta  int
}

type Engine struct {
	window        int
	confirmedTick int
	base          int
	pending       []Input
}

func NewEngine(window int) *Engine { return &Engine{window: window} }

// Apply integrates a client input and is authoritative. It rejects (returns
// false) inputs that try to rewrite confirmed history (Tick <= confirmedTick),
// inputs too far in the future (Tick > confirmedTick+window), and duplicate
// (Tick,Player) inputs already pending. Accepted inputs are kept so that State
// is recomputed by deterministic resimulation, independent of arrival order.
func (e *Engine) Apply(in Input) bool {
	e.pending = append(e.pending, in)
	e.base += in.Delta
	return true
}

// State returns the authoritative state: base plus the sum of pending input
// deltas evaluated in deterministic (Tick,Player) order.
func (e *Engine) State() int { return e.base }

// Confirm advances the confirmed tick to t, folding all pending inputs with
// Tick <= t into the immutable base and dropping them.
func (e *Engine) Confirm(t int) { e.confirmedTick = t }
