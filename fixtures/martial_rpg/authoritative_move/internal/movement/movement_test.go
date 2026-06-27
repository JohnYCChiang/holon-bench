package movement

import "testing"

func TestMoveWithinSpeedAllowed(t *testing.T) {
	got := ResolveMove(MoveRequest{Current: Vec2{0, 0}, Desired: Vec2{2, 3}, MaxSpeed: 5})
	if got != (Vec2{2, 3}) {
		t.Fatalf("got %+v, want {2 3}", got)
	}
}

func TestTeleportClamped(t *testing.T) {
	got := ResolveMove(MoveRequest{Current: Vec2{0, 0}, Desired: Vec2{100, 0}, MaxSpeed: 4})
	if got != (Vec2{4, 0}) {
		t.Fatalf("got %+v, want {4 0}", got)
	}
}

func TestNegativeDirectionClamped(t *testing.T) {
	got := ResolveMove(MoveRequest{Current: Vec2{10, 10}, Desired: Vec2{-50, 10}, MaxSpeed: 3})
	if got != (Vec2{7, 10}) {
		t.Fatalf("got %+v, want {7 10}", got)
	}
}
