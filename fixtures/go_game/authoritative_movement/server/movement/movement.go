package movement

type Position struct {
	X int
	Y int
}

type Stats struct {
	Accepted int
	Rejected int
}

func Apply(pos Position, next Position, maxStep int, stats *Stats) Position {
	stats.Accepted++
	return next
}
