package tick

import (
	"context"
	"time"
)

type Loop struct {
	Interval time.Duration
	Step     func()
}

func (l Loop) Run(ctx context.Context) {
	ticker := time.NewTicker(l.Interval)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			l.Step()
		}
	}
}
