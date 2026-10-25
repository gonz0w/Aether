# Random helper use from actual worker contexts (before implementation)

The selected OpenZFS helper is stable and scoped to a domain, but prior component
cases called it from the primary context. Before real engine workers, demonstrate
actual child draws, shared quota, close and whole-domain fatality. No kernel/SDK/
helper implementation changes. Reuse sealed guarded SDK and exact CDDL helper.

A bare native child gets a separately mapped4KiB stack and4KiB FS/cookie storage;
it has no production musl TCB and calls no other libc operation. The selected draw
helper needs no libc TLS on this initialized path; _Exit's direct transport must
terminate the whole domain when a retired helper is called from the child.
Kernel validation, slots and four-admission budget remain unchanged. The parent
initializes first and does not mutate helper phase until confirmed child stop,
so these tests do not qualify concurrent init/fini races. Child completion precedes
native retirement and stack/FS unmap. Never reuse a running or retained child range.

Positive child helper draw must leave both legacy primary fixture oracles intact.
Child debit must cause expected parent quota exhaustion125; child close must reject
parent draw125; calling after fini from a child must terminate the whole domain125,
not merely leave a stopped child. Exact paired terminal records/panic are required.
Preserve current source/pin/SDK bytes, source/tool/command/time/artifact receipts,
all attempts and own VMs. Run host/scoped checks; bind unchanged kernel to prior
required regressions. No random bytes/digests or authority are printed. New original
probe/recipes are BSD-2-Clause; selected CDDL helper/notices remain verbatim.

Simplicity/security: extend only the existing component fixture with real child
execution; no new scheduling or service framework. These cases validate an actual
engine usage pattern before widening memory/thread admission. They do not certify
POSIX TCB behavior, cryptographic quality or general service lifecycle. The engine
still cannot start within current8-MiB/two-child/four-admission limits.
