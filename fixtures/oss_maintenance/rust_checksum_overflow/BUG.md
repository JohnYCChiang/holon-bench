# Bug report: `checksum` panics on long inputs

`checksum(data: &[u8]) -> u32` computes a 32-bit rolling checksum. The contract
says the arithmetic **wraps modulo 2^32** and the function must never panic. A
user reports a crash on a normal-length input:

```
thread 'main' panicked at 'attempt to multiply with overflow', src/lib.rs:12:9
```

The state is a `u32` updated with `state = state * 31 + b`. After enough bytes
that multiply overflows `u32`, and in a debug build the overflow panics instead
of wrapping.

Expected: the running state wraps modulo 2^32 (no panic), so any byte slice
produces a defined checksum. For example, `checksum(b"holon-bench-overflow-checksum-input")`
must return `1621673765`.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`checksum` signature and the multiply-add recurrence), and **leave behind a
regression test** that pins the wrapping behavior.
