package movement

// Vec2 is an integer grid position.
type Vec2 struct {
	X int
	Y int
}

// MoveRequest is a client-proposed move. Desired is whatever the client wants;
// the server must clamp the per-axis displacement to MaxSpeed.
type MoveRequest struct {
	Current  Vec2
	Desired  Vec2
	MaxSpeed int
}

// ResolveMove returns the authoritative new position. Per-axis displacement is
// clamped to [-MaxSpeed, MaxSpeed] so a client cannot teleport. A negative
// MaxSpeed is treated as 0 (no movement).
func ResolveMove(req MoveRequest) Vec2 {
	return req.Desired // BUG: trusts the client's desired position (teleport)
}
