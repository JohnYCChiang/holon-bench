package capture

// CapturePoint is the authoritative state of a control point. Progress runs from
// 0 (fully held by defenders) to 100 (captured by attackers). ClientProgress is
// the client's claimed value and must never be trusted.
type CapturePoint struct {
	Progress       int
	ClientProgress int
}

// Advance returns the point's new progress after one fixed tick given the number
// of `attackers` and `defenders` standing on it and the maximum `rate` of change
// per tick. The net contribution is (attackers-defenders), clamped to
// [-rate, rate] (a negative `rate` is treated as 0). An equal contest (net 0)
// locks the point. Progress is clamped to [0, 100]. ClientProgress is ignored.
func Advance(p CapturePoint, attackers, defenders, rate int) int {
	return p.ClientProgress + (attackers - defenders) // BUG: trusts client, no rate cap or clamp
}
