# Scoped self-review

Independent review and companion acceptance remain outstanding.

- A Child record owns execution and child lifetime metadata together. Domain
  capability, admission counter and mappings remain outside it.
- Dispatch still validates authority/parent/arguments first. Retirement keeps
  absent/stale/live-or-pending precedence and mutates only on success.
- Save/restore, ticks, waits, wake, pins and clear-TID now reference the embedded
  Execution. Scheduler selection/order and one-child limits are unchanged.
- Admission replaces an unused record; exit stops it; reclaim clears the complete
  record after stop and mapping cleanup. No new reference survives reclamation.
- New tests verify all rejected records unchanged, full reset, peer isolation and
  FX alignment in an array. The existing same-ID, stale, pin and fault target
  regressions remain selected against frozen changed kernel sources.
- This is preparation for bounded concurrent slots; no second child, new ABI,
  capacity, policy, sibling change or multiple-waiter support is claimed.
