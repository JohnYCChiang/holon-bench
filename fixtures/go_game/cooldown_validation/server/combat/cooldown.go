package combat

type Validator struct {
	Cooldown int
	NextTick map[string]int
}

type Result struct {
	Accepted bool
	Rejected bool
}

func (v *Validator) Apply(player string, tick int) Result {
	if v.NextTick == nil {
		v.NextTick = map[string]int{}
	}
	return Result{Accepted: true}
}
