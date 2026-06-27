package dodge

import "testing"

func TestIFrameNegatesHit(t *testing.T) {
	s := DodgeState{HP: 100, DodgeTick: 10, IFrames: 5}
	if hp := ResolveHit(s, 12, 40); hp != 100 { // 12 within [10,15)
		t.Fatalf("hit during i-frames should be negated: hp=%d want 100", hp)
	}
}

func TestHitAfterIFramesLands(t *testing.T) {
	s := DodgeState{HP: 100, DodgeTick: 10, IFrames: 5}
	if hp := ResolveHit(s, 15, 40); hp != 60 { // 15 == DodgeTick+IFrames, window exclusive
		t.Fatalf("hit after window should land: hp=%d want 60", hp)
	}
}

func TestClientInvulnerabilityIgnored(t *testing.T) {
	s := DodgeState{HP: 100, DodgeTick: 10, IFrames: 5, ClientInvulnerable: true}
	if hp := ResolveHit(s, 50, 30); hp != 70 { // far outside window; client claims invuln
		t.Fatalf("client invuln was trusted: hp=%d want 70", hp)
	}
}
