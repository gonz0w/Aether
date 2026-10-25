# Bounded wake-count contract

New pair-only 0x2800c: RDI current domain thread capability, RSI writable aligned
u32 wait address, RDX count 0..INT_MAX; R10/R8/R9 reserved zero. Authority -13;
off-pair -38 after authority; zero/unaligned address, excessive count/reserved -22;
unmapped/nonwritable address -14. Validate all inputs before mutation even count0.
Any context holding the domain grant may wake. Match only this owner's registrations.
Return number woken, at most count. Count0 wakes none. Iterate parent then child
records deterministically; no FIFO/fairness promise. Expired registrations complete
as timeout before selection and consume no wake budget. Preserve elapsed time.
Existing 0x28004 and clear-TID retain wake-all semantics and bytes/contracts.

No queue allocation, global authority, new waiting slots or requeue. Existing
IF=0 validation/commit and wait-address pins apply. Two children parked on one
word must remain parked after zero/invalid calls, wake exactly one, then remaining
one; no-waiter call returns0. An unlimited-wake mutant must fail assertion201.
Host tests exercise count, nonmatching keys and timeout precedence. Run full old
thread, memory/image/M4/init suites and extended pair cases on frozen sources.
Update native reference, workflow and STATE. No sibling/pin/upstream changes.
This is the prerequisite for requeue, not multiple-waiter musl acceptance.
