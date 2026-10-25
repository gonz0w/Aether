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

Format gate: initial unqualified clang-format used LLVM default instead of required project YAML (diagnostics returned in this session); correct YAML passes maintained backend. Preserve hash-bound historical regression.c and sealed packet; create formatted current witness and rerun UTC overlap/serial in fresh cycle attempt2. Only whitespace/line-based diagnostic numbers change; 870 and semantic oracles unchanged.

Final gate attempt1: quality/pins, project C format and both syntax checks passed; whitespace command did not start because owned runner requires absolute executables. Correct git to /usr/bin/git; preserve attempt1 process receipt, rerun in fresh checks-2 root.

Final disposition: ten elapsed and six final UTC cases pass, with complete owned
native cleanup; original old-cycle expected870 remains a denial witness. Both
interpreters pass115 elapsed +50 UTC +24 ordered UTC trace corruptions, SDK/CLI
controls and eight UTC builder controls (obsolete base rejects). Elapsed and UTC
minimum/current/standalone archives match. New immutable294/343-member v3 packets
retain old candidates and guarded SDK. Root Codex performed technical/source
review; independent Aether owner intake and human reader sign-off remain pending.
Quality gate verifies all three published pins and approved-draft inventory;
project YAML C format, actual minimum/current syntax and whitespace pass. No
shared adoption change. New snapshot/SDK/authority change invalidates these native
composition results; wider scheduler/stop schedules remain follow-ons.
4856 generated files/links removed after readback;3403 compact records retained;
468672512 allocated file-block bytes removed (not net-free-disk measurement).
Frozen kernel/firmware/fixtures and immutable handoffs remain. No bulk archive.
Simplicity answers: use existing per-record single-reaper ownership and atomic
publication instead of a second mutex; old list serialization is insufficient
because pending exits own that lock; remove one lock dependency without changing
quotas/protocols. UL003/015/081 remain active; no pool/persistence/SESSION closure.
