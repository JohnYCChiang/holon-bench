# Domain: Document Approval Chain (bounded context)

Implement `src/approval.py` to satisfy these rules. This aggregate enforces an ordered
approval workflow and records domain events.

## ApprovalChain (aggregate root)
- Created with a non-empty ordered list of `approvers` (`ValueError` if empty).
  Starts in state `"PENDING"` at index 0 with an empty `events` list.
- `approve(who)`:
  - Only valid while `PENDING` (`ValueError` otherwise).
  - `who` must equal the current expected approver (`approvers[index]`); otherwise
    `ValueError` (this also rejects out-of-order and duplicate approvals).
  - On success append `"Approved:<who>"` and advance the index. When the last approver
    approves, set state to `"APPROVED"` and append `"DocumentApproved"` exactly once.
- `reject(who)`:
  - Only valid while `PENDING`, and `who` must be the current expected approver
    (`ValueError` otherwise).
  - On success set state to `"REJECTED"` (terminal) and append `"Rejected:<who>"`.
- A rejected command must not mutate state.

Only edit `src/approval.py`.
