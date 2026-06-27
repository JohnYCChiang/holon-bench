# Bug report: priority queue breaks ties LIFO instead of FIFO

`PriorityQueue` pops the highest-priority value, and the contract says ties on
priority are broken by **insertion order (FIFO)** — the value pushed first
comes out first. A user reports ties come out in reverse:

```
let mut q = PriorityQueue::new();
q.push(5, "a".into());
q.push(5, "b".into());
q.pop();
// got:  Some("b")
// want: Some("a")
```

When scanning for the best element, the tie comparison keeps the *later*
insertion, so equal-priority items are served last-in-first-out.

Expected: higher priority first; equal priorities served in insertion order
(FIFO); `pop` on an empty queue returns `None`. For `push (1,a) (3,b) (1,c)
(3,d)` the pop order is `b, d, a, c`.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`new`/`push`/`pop`/`len`/`is_empty` API), and **leave behind a regression test**.
