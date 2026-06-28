package weather

// Cycle is a deterministic weather schedule. Weather advances through a fixed
// ordered list of phases, each lasting Duration ticks, then repeats. At(tick)
// is a pure function of the tick so replays and late-joining clients always
// observe identical weather. Within a single phase window the weather is
// constant.
type Cycle struct {
	phases   []string
	duration int
}

func NewCycle(phases []string, duration int) *Cycle {
	return &Cycle{phases: phases, duration: duration}
}

// At returns the weather phase active at the given tick. An empty schedule, a
// non-positive duration, or a negative tick returns "".
func (c *Cycle) At(tick int) string {
	if len(c.phases) == 0 || c.duration <= 0 || tick < 0 {
		return ""
	}
	// BUG: indexes by the position *within* a window instead of the window
	// number, so weather changes every tick and never holds for Duration ticks.
	idx := (tick % c.duration) % len(c.phases)
	return c.phases[idx]
}
