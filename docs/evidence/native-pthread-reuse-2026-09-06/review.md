# Scoped self-review

Independent review and companion acceptance remain outstanding.

- Retirement validates the current domain thread capability and parent context
  before arguments or state changes. It takes an ID, never a user pointer.
- The child must have stopped, cleared its exit address and left no pending wait.
  Reset clears execution/TLS/FP/mask state and stack/status metadata, not mappings.
- IDs increase within the four-admission domain budget. Retirement cannot refill
  it. Invalid creations cannot consume it. New domain grants reset the budget.
- The join wrapper calls unchanged upstream __pthread_join. After successful join,
  it clears the saved handle before retirement checks and uses only the saved ID.
  Retirement failure keeps admission closed; retry cannot enter upstream with
  the freed handle. No general stale pthread_t detection is claimed.
- One child can execute at a time. This is a bounded conformance adapter, not a
  multi-child pool, production userland adoption or complete POSIX threading.
- Same-ID mutation must hit assertion 233; existing authority, fault, guard,
  allocation-pressure and live-pin cases remain selected.
