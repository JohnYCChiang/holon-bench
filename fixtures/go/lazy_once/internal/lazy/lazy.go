package lazy

// Value computes a result exactly once and caches it. Get must be safe for
// concurrent use and must invoke init at most once.
type Value struct {
	init   func() int
	cached int
	done   bool
}

func New(init func() int) *Value {
	return &Value{init: init}
}

// Get returns the cached value, computing it on first use.
func (v *Value) Get() int {
	if !v.done {
		v.cached = v.init()
		v.done = true
	}
	return v.cached
}
