# Bug report: `contains` rejects addresses for a CIDR written with host bits

`cidr.contains(cidr, ip)` reports whether an IPv4 address is inside a CIDR block.
Operators often write the network loosely, with host bits set, e.g.
`"192.168.1.10/24"` to mean "the /24 around 192.168.1.10". A user reports:

```
>>> from src.cidr import contains
>>> contains("192.168.1.10/24", "192.168.1.200")
False        # expected True: .200 is in 192.168.1.0/24
```

The masked candidate (`192.168.1.0`) is compared against the **raw** network
integer (`192.168.1.10`) instead of the network's masked address, so any CIDR
whose written address has host bits set rejects valid members.

Expected: the network address is normalized (masked) before comparison, so
`contains` only depends on the prefix length, not on whether the operator wrote
the exact network address.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`contains(cidr, ip)` API), and **leave behind a regression test** that pins the
host-bits normalization.
