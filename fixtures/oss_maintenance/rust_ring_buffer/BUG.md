# Bug report: `RingBuffer::to_vec` panics / returns garbage after wrap-around

`RingBuffer<T>` is a fixed-capacity ring buffer. `push` appends a value, and
once the buffer is full it **overwrites the oldest** element. `to_vec` returns
the live elements in **oldest → newest** order.

A user reports a panic as soon as the buffer wraps past its capacity:

```
let mut rb = RingBuffer::new(3);
for x in [1, 2, 3, 4, 5] { rb.push(x); }
rb.to_vec();
// thread 'main' panicked at 'index out of bounds: the len is 3 but the index is 3'
// want: [3, 4, 5]
```

Before wrap (`new(3)` then push `1,2`) `to_vec` correctly returns `[1, 2]`, but
once the read index passes the end of the backing storage it is no longer
reduced modulo the capacity.

Expected: `to_vec` always returns the current elements oldest → newest, e.g.
`[3, 4, 5]` above, no matter how many times the buffer has wrapped.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`RingBuffer::new`/`push`/`to_vec` API and the overwrite-oldest semantics), and
**leave behind a regression test** that pins the wrap-around read order.
