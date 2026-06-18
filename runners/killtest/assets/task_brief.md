# Task brief — SortedUniqList (identical for both arms)

Source of truth: `tao-killtest-prereg-v0` Appendix A.1 (FROZEN). This brief is
identical in both arms; only the *mechanics* doc differs.

Implement a bounded sorted unique integer list, `SortedUniqList`.

Representation: a sequence of integers. Invariant: elements strictly ascending
(which implies uniqueness) AND size ≤ CAP, with **CAP = 64**.

Operations (all pure, total, monomorphic over canonical integers):

- `empty  : SortedUniqList`
- `insert : Int → SortedUniqList → SortedUniqList`
  inserting a present element, or inserting into a full list, returns the list
  unchanged.
- `member : Int → SortedUniqList → Bool`
- `size   : SortedUniqList → Int`

Laws to uphold:

- **L-ord**: adjacent elements of any constructed value are strictly ascending.
- **L-mem**: `member x (insert x s)` unless `size s = CAP ∧ ¬member x s`.
- **L-idem**: `insert x (insert x s) = insert x s`.
- **L-comm**: `insert a (insert b s) = insert b (insert a s)`.
- **L-size**: `0 ≤ size s ≤ CAP`; `size (insert x s) ∈ {size s, size s + 1}`.

Green = the full acceptance suite passes under the trusted toolchain. A held-out
hidden + mutation suite (never shown) also runs at scoring time. Make the
smallest correct solution; do not edit the suites.
