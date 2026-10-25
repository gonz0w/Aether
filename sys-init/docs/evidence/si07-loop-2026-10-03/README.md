# Quiescent ABI22 request loop — 2026-10-03

Seven fresh native cases pass. The maintained sustained owner accepts one-byte
r (run the fixed bytecount workload) or h (halt) before allocating any worker.
It accepts halt before the first cycle and after each complete cycle. Successful
cycles retain explicit protocol retirement, observed terminals, reverse cleanup,
backend EOF, reclamation and stale-handle denial before the next request. The
separate fifth-cycle halt prompt and five-cycle admission cutoff are removed.
No new syscall, owner abstraction, dependency, service or unsafe block is added.

| Native case | Expected result |
| --- | --- |
| halt-zero | Authorized halt with zero workers/reclaims |
| halt-one | One useful cycle, exact output/readback, 0/0/17 terminals, three reclaims, halt |
| halt-six | Six useful cycles and 18 reclaims, then halt; passes the former five-cycle cutoff |
| queued-halt | r and h supplied together; one complete cycle and three reclaims before halt |
| invalid | x rejects before admission, no ordinary terminals or successful halt |
| omitted-close | Private image omits UART close; final halt returns -16 (busy), explicit control marker, no halt |
| exhausted-admission | Private epoch forced to65536; r rejects before admission, no terminals/halt |

The native runner checks exact terminal order, request/completion counts and
reclaim counts. Input is delayed200ms after each prompt to exercise waiting;
queued-halt instead writes both bytes together. This proves deferred handling of
buffered intent, not the precise instant of arrival inside a backend effect.
Every case retains the existing startup idle witness beyond3000 ticks. That
30-second fixture probe remains test behavior, not a proposed product boot delay.

The normal experimental image is10152 bytes (previous10192), below
16384. Both normal and omitted-close linked stack bounds are2696/4088 usable;
exhaustion image1077 bytes and336 stack. No mapping/stack limit changed. The linked
inspection charges both memcpy/memset at indirect calls. RIP cells are resolved
from raw image bytes; the two RBX calls at0x401360/0x401371 load memset at0x401359,
with no intervening write and callee-saved RBX. Normal cell0x4027a0/control0x4027c0
resolve to memset. There are no indirect jumps; exhaustion has no indirect calls.
This scoped inspection is not formal whole-program or kernel-stack verification.
Five legacy ABI9 variants rebuild byte-identically. ABI17 sources are unchanged.

Private epochs remain1..65535, with no wrap or reset. The loop admits up to that
protocol limit, then still permits h; another r rejects before acquiring resources.
The forced exhaustion case tests the guard, not65535 executed cycles. This is a
finite identifier budget for normal command reuse, not a new restart policy or
an indefinite-uptime claim. Existing cohort and error rules remain authoritative.
Malformed input and ambiguous protocol/cleanup failures remain fail-closed fixture
failures, never successful shutdown or effect replay.

## Inputs, review and process

The preceding sealed si07-owner packet supplies the full frozen source archive,
verified local dependencies, application envelope and build recipes. Its seal and
all copied dependency hashes were checked before use. Only success.rs and
sustained_owner.rs change in the main staged source. The private omitted-close
source is retained separately and never promoted. Compiler, Zig and QEMU identities
match the prior pins. Exact commands, source snapshots, linked/raw/envelope bytes,
ISO hashes, serial and raw QEMU logs are retained. ISOs/firmware remain private
under out. No sibling source read or write, standard pin change, or new platform
campaign was needed. Drivers are dated internal recipes, not installed CLIs.
All native cases completed without a failed build or rerun in this slice.

Simplicity review: fixed-five behavior is simpler but cannot implement arbitrary
quiescent shutdown. Reading the request before resource acquisition handles both
initial and subsequent shutdown with one branch and removes the separate halt
input path. Existing paired ownership and bounded protocol behavior are reused;
there is no control service or cancellation framework. The new SI07 request-ready
marker deliberately replaces the former command-ready/halt-ready fixture prompts
in the new runner only. Older sealed fixtures and kernel markers are unchanged.
Plain ASCII output stays within the existing internal Experience adoption scope;
this console is developer-only, not authenticated operator access (ID-01).
O-01–05, I-01/03–06, E-01–08 and existing resource/measurement limits apply as in
the preceding owner record. No new standards exception or full conformance claim.

Remaining BG-067 work: focused partial/unknown reply and cleanup-failure behavior,
idle/wakeup schedules beyond these delayed/buffered cases, then useful-session
integration and full handoff disposition. A general shell/operator CLI, authenticated
shutdown, mid-effect interruption, production failure recovery and infinite uptime
are not implemented by this request loop. Broader features remain shelved.
Quality inventory, prototype guide, current planning and handoff are updated.
Independent review and release acceptance remain separate.

All ten offline gates pass in run-k_a6cy14 with checked sources unchanged.
validation.json and validation/ retain the report. git diff --check passes.
sha256.json excludes only itself.
