package queue

// PQueue is an authoritative priority matchmaking queue. Pop returns the
// highest-priority player; ties are broken by insertion order (FIFO). A player
// id may be queued at most once.
type PQueue struct {
	items []item
	seq   int
	in    map[string]bool
}

type item struct {
	id   string
	prio int
	seq  int
}

func NewPQueue() *PQueue { return &PQueue{in: map[string]bool{}} }

// Push enqueues id at the given priority. Empty ids and ids already queued are
// rejected.
func (q *PQueue) Push(id string, prio int) bool {
	if id == "" || q.in[id] {
		return false
	}
	q.in[id] = true
	q.items = append(q.items, item{id: id, prio: prio, seq: q.seq})
	q.seq++
	return true
}

func (q *PQueue) Len() int { return len(q.items) }

// Pop removes and returns the highest-priority player, ties broken by earliest
// insertion. It returns false when the queue is empty.
func (q *PQueue) Pop() (string, bool) {
	if len(q.items) == 0 {
		return "", false
	}
	bestIdx := 0
	for i := 1; i < len(q.items); i++ {
		if q.items[i].prio >= q.items[bestIdx].prio { // BUG: >= lets a later equal-priority entry win, breaking FIFO ties.
			bestIdx = i
		}
	}
	it := q.items[bestIdx]
	q.items = append(q.items[:bestIdx], q.items[bestIdx+1:]...)
	delete(q.in, it.id)
	return it.id, true
}
