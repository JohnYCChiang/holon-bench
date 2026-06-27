# Domain: Auction (bounded context)

Implement `src/auction.py`. An `Auction` accepts ascending bids that respect a
minimum increment, then closes to a winner.

## Auction (aggregate root)
- Created with a non-negative integer `start_price` and a positive integer
  `min_increment` (`ValueError` otherwise).
- Starts open (`closed == False`) with `highest_bid is None`,
  `highest_bidder is None`, and an empty `events` list.
- `bid(bidder, amount)`:
  - Invariant: the auction must be open (`ValueError`).
  - Invariant: `bidder` must be non-empty (`ValueError`).
  - First bid: `amount` must be `>= start_price` (`ValueError`).
  - Later bids: the current highest bidder may not raise their own bid
    (`ValueError`), and `amount` must be `>= highest_bid + min_increment`
    (`ValueError`).
  - A rejected command must not mutate state.
  - On success: set `highest_bid` and `highest_bidder`, append a `"BidPlaced"`
    event.
- `close()`:
  - Invariant: the auction must be open (`ValueError`); closing twice is rejected.
  - On success: set `closed = True`. If there is a highest bidder, append an
    `"AuctionWon"` event. Returns the winning bidder (or `None` if no bids).
- `winner()` returns the winning bidder; raises `ValueError` if still open.

Only edit `src/auction.py`.
