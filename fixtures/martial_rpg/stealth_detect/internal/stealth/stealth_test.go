package stealth

import "testing"

func TestDetectsWithinRadius(t *testing.T) {
	if !Detect(Probe{ObserverX: 0, ObserverY: 0, TargetX: 2, TargetY: 1, Radius: 3}) {
		t.Fatalf("target within radius was not detected")
	}
}

func TestNotDetectedOutsideRadius(t *testing.T) {
	if Detect(Probe{ObserverX: 0, ObserverY: 0, TargetX: 10, TargetY: 0, Radius: 3}) {
		t.Fatalf("target outside radius was detected")
	}
}

func TestIgnoresClientFlagWhenFar(t *testing.T) {
	if Detect(Probe{ObserverX: 0, ObserverY: 0, TargetX: 100, TargetY: 100, Radius: 5, ClientDetected: true}) {
		t.Fatalf("client detection flag was trusted")
	}
}
