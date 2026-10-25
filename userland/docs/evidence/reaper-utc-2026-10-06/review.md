# UL-003/015/081 detached retirement fix — before code

Aether's pinned ordered-exit witness confirms A stopped/unretired, B holding
musl list lock awaiting permission, reaper awaiting that lock. Fix local runtime
metadata synchronization; preserve native stop-before-unmap-before-retire, quotas
82/512/8192, upstream exit/list bodies, original sealed candidates and base SDK.

Smallest reviewed design: make record thread publication/free pointer atomic.
Creators/joiners remain serialized by upstream list lock; detached retirement
uses its pending/published release boundary and exclusively owned record until
confirmed stop. Clear pending/publication and decrement live before release-free
pointer publication. The reaper must never acquire musl's list lock while cleaning
an already stopped/unlinked detached owner. Avoid adding a second lock hierarchy.
Review metadata snapshots and creation/reuse happens-before; no plain thread
pointer race or free-before-unmap/retire. Broader alternative separate record lock
adds a hierarchy that is unnecessary for sole-reaper per-record ownership.

Before/after native ordered A/B exit test, same native upstream lock/exit bodies;
old archive must exhibit exact870 cycle, corrected archive must retire A while B
holds original list lock and then collect B. Serial controls, repeated overlaps,
normal/stop/clock denial/lifecycle/busy/exhaustion and UTC native regressions.
Actual minimum/current/standalone builds; immutable new elapsed/UTC handoffs.
Use current frozen kernel/source/firmware, strict C17, bounds and unchanged owned
runner; tools complete before VM ownership. Tools120s, guest35s/owner45s,
UART1MiB/stderr4MiB, terminate/reap, no forced kill success. Preserve every attempt,
source, compiler flags/artifact/source/tool hashes and compact cleanup receipts.

Foundations O/I/E, Distribution applicability, approved TD/TC/TE and C/CP,
local SE-01–05 apply. No native/ABI/kernel/sibling changes or standards pin update.
Original BSD2/upstream musl terms retained. Root agent technical review; external
reader/owner acceptance pending. Deferred human reader is not a coding block.
This fixes a confirmed cycle, not attribution of the earlier engine timeout.

First old-cycle run produced exact870 and peer0, but oracle incorrectly required peer870. Corrected allowed peer success for the deliberately inert small owner; primary870/supervisor401/zero reclaims remain mandatory. Original failed oracle/native receipt preserved. Add all affected runtime regression cases in fresh attempt2.

Attempt2: six before/after/native cases passed. Lifecycle link failed because substring `cycle` matched `lifecycle` and enabled regression-only wrappers. Correct exact case membership; no runtime change. Preserve attempt2 and rerun fresh all ten.

Attempt3: eight before/after/runtime cases passed, including lifecycle and full512 exhaustion. Disabled image build rejected duplicate clock flags. Remove duplicate explicit flag, preserve eight completed receipts and run only disabled/early in fresh attempt4. Runtime/provider bytes unchanged.

Technical review (root Codex, 2026-10-06): creators hold actual musl list lock
through native descriptor installation. Publication is atomic and occurs after
all record metadata and live/admission increments; trampoline and sole reaper
acquire that publication. Exiting detached owner holds the same lock, publishes
pending, and remains parked until reaper permission. Reaper owns that pending
record exclusively until native status confirms stop, unmap succeeds and retirement
succeeds. It never reads the unmapped TCB. Reaper resets pending/publication,
decrements live, then atomically publishes thread=NULL last. Creator's acquire
load of NULL orders all prior cleanup before any reuse writes. Join reads atomic
thread under creator/list serialization; detached tag is stable until reuse and
rejects before TCB access. Reaper does not write the plain id/base/bytes/detached/
joining metadata; no free-time plain-metadata race is introduced. Joinable cleanup
still holds list lock, so its existing ordering stays safe. Finish closes admission
under list lock; observing live=1 can precede final NULL publication but it joins
reaper, so successful finish still waits for all cleanup and live0. New pending
exits can never reintroduce a reaper/list dependency during retirement. Atomics
use default sequential consistency; no additional mutex or native authority.

Reuse impact: calendar/provider/wrapper source bytes unchanged from UTC-v2 and
prior Gregorian3040/UBSan/injected-failure controls retain their original scope.
New native UTC composition tests are required because archive base changed.
No claim that this reproduces or attributes the earlier engine leap timeout.
Independent Aether intake and human reader review remain pending; UL stories
remain open. Scope/docs: update current STATE/BACKLOG/ROADMAP, architecture record
ownership and maintained recipe pointers; no shared adoption/pin change.

Initial seal preparation failed before any seal: builder leaves runtime.h in maintained source, not build output. Removed only newly created unsealed packet, corrected header source, retained failed sealer.

Final UTC composition: maintained builder pins294-member corrected elapsed seal
and rejects obsolete v2. Provider/calendar/wrapper/test source bytes remain exact,
with explicit reused source/receipt identities. Four fresh date/source-policy VMs
and two ordered/serial VMs pass; formatted witness rerun preserves earlier frozen
attempt. Both interpreters reject50+24 trace corruptions and eight builder controls.
Minimum/current/standalone archive693518d97acafe99f427cae5b42b5cc7aea7f0e8656c17f185fc8c24a0e06150
matches. New343-member immutable UTC v3; independent Aether intake/actual engine
helper reuse and reader review pending. No previous timeout attribution, source
trust, persistence, quota, ABI or wider SESSION change. Final quality/format/syntax/
whitespace/readback and compact cleanup are recorded in ../reaper-fix-2026-10-06/.
