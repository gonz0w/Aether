# Scoped self-review

0x2800c uses the existing current-domain capability gate and is unavailable outside
the pair profile. Address, writable bytes, count and reserved inputs are checked
before wake mutation. The bounded helper scans only supplied owner contexts; it
allocates nothing. With IF=0 there is no gap between validation and completion.
Expired registrations complete with timeout and preserve elapsed time without
consuming the count. Unmatched/unselected registrations remain parked and pinned.
The old operation and clear-TID call the same helper with an unlimited bound.
No wait registration, mapping or context lifecycle rules changed.

Host checks exercise two waiters, zero/one/all counts, unmatched keys and exact
timeout precedence. Target second batch parks two real children on one word;
invalid inputs and zero leave both parked, one wakes exactly one, another wakes
the other and an empty wake returns0. Invalid cap, zero/unaligned/unmapped/read-only
address, excessive count and reserved input are rejected. Unlimited-wake mutant
must hit assertion201. Existing first-batch independent wake, context state,
retire/reuse, faults and supervisor cleanup remain in the complete pair suite.

Risk: scanning order is deterministic, not FIFO/fairness. At most three local
contexts exist in the selected profile. Capability and buffer ownership stay
unchanged. Full old thread suites including concurrent musl, memory/image/M4/init
regressions were selected because wake-all is shared with clear-TID and waits.
No new dependency, sibling, pin or upstream patch. Independent review/consumer
adoption remains open. This is a wake-count primitive, not requeue or acceptance
of multiple musl condition waiters. The current libc adapter is unchanged.
