# Bounded native cat producer direction

UL-067 follows the userland CAT-01–08 request. The producer experiments cover
three-stream bootstrap/copy, direct owner-selected startup, bounded argument
diagnostics and complete-error cleanup with a conformance client. They do not
execute Toybox, expose caller-driven name admission or accept CAT-01–08.
Userland owns Toybox initialization, process-local mask/stdio and finalization;
Aether owns exact role/transport and native lifecycle enforcement. Existing
[NATIVE-COMMAND-IO](NATIVE-COMMAND-IO.md) modes and UL-059 handoff pins stay intact.

## AECAT001 prerequisite

A private owner-to-client 128-byte carrier has a 32-byte header: magic AECAT001,
little-endian count3 and native generation, then 16 zero bytes. Three ordered 32-byte
records hold role, generation reference, descriptor, rights, capacity, then 12 zeros:

| Role | Descriptor | Rights | Capacity | Reference |
| --- | --- | --- | --- | --- |
| Input1 | 0 | read1 | 32 | 0x76000000 + generation |
| Output2 | 1 | write2 | 32 | 0x76010000 + generation |
| Diagnostic3 | 2 | write2 | 256 | 0x76020000 + generation |

Read all bytes and validate every header/record field before publishing any binding.
Unknown/missing/duplicate/misordered/stale authority rejects; no invented diagnostic
sink is available on malformed bootstrap. The current selected rejections are
count2 and third-role rights3, duplicate fd1 or stale reference. Failure terminates
with fixture110 and zero I/O; the owner checks this independently. These selected
full-carrier cases do not establish exhaustive truncation or arbitrary corruption.

Use the existing 32-byte read/write/consuming-close protocol through explicitly
scoped channels. Input cannot be written, output/diagnostics cannot be read by the
client. All backend bytes remain independently readable by the authorized verifier.
References/FD numbers/mask values alone never confer authority. The fixed unsigned
0077 initial process mask is still a proposed userland-state decision; this carrier
contains no mask field and no umask syscall or successful stub is introduced.

## Executable scope and evidence

The client is `user/native-command/cat-client.c`, using actual musl read/write/close,
with a private TLS check. It copies empty or exact 32-byte binary fixture input,
including NUL/high bytes. The short mode returns at most 7 bytes per read and 3 per
write. The diagnostic mode independently writes a two-byte D-LF sentinel, not a
proposed Toybox/user-facing diagnostic. Input is preserved, stdout is exact input
and diagnostics stay empty except in that sentinel case. Output capacity remains
32 even though the reused backend storage allocation is larger.

Owner `cat-roles.rs` and backend `user/native-files/streams.rs` keep local state.
Two generations run client slot0 and backend slot1, with four native reclaims; no
slot2 admission or collection is claimed. Require explicit three closes on valid
startup, request EOF at terminal, exact positions/bytes, all backend closes and
stale-handle denial. On invalid startup, no bindings publish and the owner releases
its backend handles. Skip/corrupt-copy, omitted diagnostic close and early-binding
publication controls reject at1505/1505/1503/1502 respectively.

Run the complete existing command suite:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build SDK --tools-lock LOCK
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The [evidence](evidence/cat-roles-2026-09-07/README.md) records exact pinned SDK/tool
paths, commands, case names, artifacts and regressions. `cat-roles-*` cases select
owner cfg cat_roles and parent CAT_ROLES; the backend uses runner_streams+cat_roles.
The empty case adds cat_empty to owner/backend. The existing local boot oracle is
selected explicitly; it adds no kernel resource capacity or invocation.

## Remaining CAT work

The direct admission section below qualifies the owner-selected conformance image.
Actual Toybox artifact selection, bounded argument rejection, runtime initialization/
finalization and error/abnormal-stop verification remain to be qualified.
CAT-01 admission, CAT-03 argument rejection, CAT-04 real SDK initialization,
CAT-05 errors/unknown replies and CAT-06 Toybox flush/finalization are unqualified.
CAT-02/07/08 have only this prerequisite and old regressions, not native Toybox
acceptance. Userland must independently review/pin/build the eventual producer
return bundle. No filename/options/package/POSIX/TTY or release support follows.

## Direct owner-selected admission

`cat-roles-admit-*` adds cfg cat_admission and client CAT_ADMISSION. The owner
selects the supplied first image capability and invokes the existing native factory
for slot0 with exactly argv=[cat], env=[LC_ALL=C]. This is a fixed owner template,
not a caller-facing name lookup, new runner launch frame or Toybox artifact.
The direct client/backend resource inventory remains four reclaims in two generations.

Before channel reservation, the owner gate checks argc1/envc1, exact zero-padded
cat and LC_ALL=C slots, and zero unused strings. Same-gate probes reject changed
name (-2), extra argc, changed environment and unused padding (-22). A name-gate
bypass control fails1510 before client admission. The image capability, not these
strings, supplies authority. Validating a template does not grant authority to an
untrusted caller or establish a new package/name registry.

With reserved transfer endpoints, actual native argc5 admission must return EINVAL
and retain both endpoint authorities. Valid admission then transfers them; owner
close attempts must return EACCES. Failure paths release reserved endpoints. The
owner overwrites its Args storage after native admission and before role delivery.
The client waits for bootstrap and independently checks argc/argv terminator, cat,
LC_ALL=C, sole environment entry and TLS, proving the copied startup survives.
A post-gate argv corruption control returns client109/owner1501 before input I/O.
Malformed role composition returns110 with no published binding or I/O.

Selected full/empty/short-copy cases retain the same backend-byte, alias, EOF and
reclaim checks. [Admission evidence](evidence/cat-admission-2026-09-07/README.md)
records exact image/tool/source identities. CAT acceptance still needs actual
Toybox argument/init/finalization behavior and independent consumer review/build;
this does not expose caller-driven cat admission or accept the Toybox package.

## Bounded extra-argument diagnostics

The separately selected cat_usage template includes one pinned, zero-padded32-byte
argument artifact with argc2. Default direct admission remains argc1. The owner
checks the exact selected template before reservation; no generic name lookup or
arbitrary caller admission is added. AECAT001 and native Args wire layouts remain.

After identity and complete role validation, the conformance client rejects any
extra argument before reading stdin. The proposed fixture is:

```text
cat: this profile accepts stdin only
```

These 37 bytes are ASCII with LF, no styling or argument echo, and go only to the
explicit diagnostic binding. The authoritative fixture is
`user/native-command/cat-usage.txt`. This is Aether's producer proposal, not upstream
Toybox output or independent userland text acceptance. Userland owns its actual
bounded gate and eventual adoption. Options, filename, empty operand and stdin
operand tests do not advertise support for those forms.

The owner requires status64, no input requests, empty stdout, exact diagnostic,
three closes, request EOF, backend readback/stale denial and four reclaims across
two generations. Selected operands: -, -u, -n, example.txt, --help, --version,
--unknown and empty string. Short diagnostic writes continue only the suffix.
Malformed role composition requires110 with no diagnostic or binding publication.
Skipped/corrupt diagnostic, attempted input read and omitted close reject at
1505/1505/1520/1503. Status64 alone is never the delivery/cleanup oracle.

Existing nonzero command status is retained through final cleanup in this fixture;
unexpected delivery/close errors cannot pass its complete-output/close verifier.
Injected I/O errors, unknown replies and Toybox callbacks/flush/finalization still
need separate witnesses. [Evidence](evidence/cat-usage-2026-09-07/README.md) retains
exact operand/text/SDK/source identities. This does not accept CAT-03 or UL-067
on behalf of the actual Toybox consumer.

## Complete-error replies and cleanup

The opt-in `cat-roles-error-*` conformance profiles inject one complete, zero-padded
EIO reply. Read failure after11 input bytes leaves exactly11 output bytes. Write
failure after11 committed output bytes leaves22 input bytes consumed and exactly11
output bytes. Both stop all subsequent data requests, retain empty diagnostics,
return1 and close all roles. Diagnostic failure after16 committed bytes retains
usage64, no input/stdout traffic and precisely that diagnostic prefix. These are
transport/cleanup witnesses; they do not propose a Toybox I/O diagnostic or accept
its final text/status behavior.

AECAT001 consuming close now explicitly permits complete EIO as acknowledgment
of alias consumption. The adapter still retires the local binding before exchange;
this complete reply allows remaining roles to close. Each of input/output/diagnostic
close is exercised separately: failure promotes a zero result to1. Diagnostic
close after invalid invocation retains64 and the complete usage text. Remote alias
consumption, verifier-owned backend closure and native reclaim are separately
checked. Other errors or malformed/lost replies still poison the channel; their
CAT-specific witnesses remain pending. The existing AEOUT001 rule is unchanged.

The client funnels copy errors through cleanup. The owner requires the selected
injection to occur exactly once, no later data request, exact prefixes/readback,
three consuming closes, terminal EOF, backend stale denial and four native reclaims.
Force-success, omitted-close and failed-write replay controls require exact
1501/1503/1530 rejection. No new kernel primitive or resource budget is added.
Full command and connections/inherited regressions cover the shared header change.
[Evidence](evidence/cat-errors-2026-09-07/README.md) records qualification separately.
Actual Toybox initialization, callbacks/flush, unknown outcomes, EINTR, abnormal
stop and independent consumer acceptance remain open.

## Malformed and truncated replies

`cat-roles-unknown-*` commits the first selected read/write/diagnostic/input-close
operation, then corrupts reserved byte4 or sends only16 reply bytes and closes the
actual response channel. The client must poison its transport, return1 (usage64),
retire all local bindings, and reject repeated closes with EBADF. Opt-in counters
require zero further channel traps after poison. Owner rejects every subsequent
request at1532; local retirement does not imply a confirmed remote close.

Expected consumed input/committed stdout/stderr are11/0/0 for read,11/11/0 for
write,0/0/16 for diagnostic and32/32/0 for close. The owner observes all aliases
remaining except input in the close case, verifies exact backend prefixes and
terminal EOF, then closes its backend handles and reclaims both native images.
Two generations retain four reclaims. Force-success, skipped-local-close and
cleared-poison controls require1501/1501/1532 rejection. Actual channel truncation
has no timeout-based success oracle. These are conformance-client witnesses,
not upstream Toybox or general uncertain-result recovery. EINTR, callbacks/flush,
finalization re-entry and abnormal termination remain separate work.
[Evidence](evidence/cat-unknown-2026-09-07/README.md) retains the qualified inputs.

## EINTR and completed finalization re-entry

`cat-roles-eintr-*` selects complete EINTR replies at the existing read/write/
diagnostic error points. The client must observe musl errno EINTR, stop without
retry, close all roles and preserve status1 (usage64). Exact positions remain
11/11/0,22/11/0 and0/0/16 respectively. Wrong errno returns114 and cannot pass;
retry-write and force-success controls require1530/1501 rejection. No generic
signal delivery or upstream Toybox diagnostic is claimed.

The conformance client's `finish_bindings` remembers its completed result.
`cat-roles-finalize-*` invokes it again with a different status after copy success,
usage rejection, complete close EIO or poisoned read. The second call must retain
0/64/1/1 respectively, produce no channel trap and leave every binding retired.
A reset-guard control must return113/owner1501. These tests cover completed re-entry
only: no recursive in-progress callback, thread concurrency, actual Toybox exit
hook or fflush/ferror integration is established. The helper is private to this
fixture, not a published userland finalization API. All owner byte/alias/EOF/backend
and four-reclaim checks continue. [Evidence](evidence/cat-finalize-2026-09-07/README.md)
records the qualified scope. Abnormal stop and actual Toybox/SDK integration remain.

## Abnormal termination and owner cleanup

`cat-roles-abnormal-*` faults the isolated conformance client with UD2 after
validated startup, its first copy write, or its first diagnostic write. Native
terminal detail134/kind2 must remain distinct from normal exit134/kind1. Exact
input/stdout/diagnostic positions are0/0/0,11/11/0 and0/0/16. No finalization runs;
all three owner-observed aliases remain live at terminal EOF.

A separate owner-stop profile commits the first output write, confirms live
reclaim returns EBUSY, invokes scoped stop and withholds the pending reply. It must
observe143/kind3; repeated stop preserves that terminal observation. No client
finish hook is needed. The verifier checks the11-byte output prefix, closes its
backend handles only after terminal EOF, verifies stale backend denial and reclaims
client/backend across two generations. Stale native child poll/stop/collect must
then return EBADF. These are separate observations, not remote cleanup inferred
from a client exit code.

Wrong exit/stop kind, corrupt committed prefix and skipped backend close controls
require1501/1501/1505/1506 respectively. Existing terminal markers and four-reclaim
inventory remain. [Evidence](evidence/cat-abnormal-2026-09-07/README.md) records the
selected faults and stop, not all interruption points or production supervision.
Actual Toybox/SDK startup and callback/flush/exit adaptation and independent
consumer acceptance remain open. Sys-init and userland retain policy ownership.

Forced-stop logging scope: the existing stop path emits no client terminal serial
line. The owner directly checks143/kind3 and repeated-stop stability; the harness
requires the two backend17 terminal lines and100/reclaimed4. Wrong-kind rejection
remains mandatory. No new kernel marker is introduced to satisfy the fixture.

## Real upstream native-SDK link baseline

The [build audit](evidence/toybox-native-link-2026-09-07/README.md) compiles unpatched
Toybox0.8.14 standalone cat against the same pinned native SDK: static x86_64 ELF,
80,128 bytes and21 load pages. It was not executed or admitted by the native loader.
Resolved generated headers/config are captured inputs, not a generator reproduction.
The actual config retains TOYBOX_FORK; no NOFORK shortcut skips initialization.
Disassembly confirms unsupported umask0x1005f and stdio writev0x10014 plus the direct
_xexit→_exit path. The selected xexit calls fflush_unlocked/ferror_unlocked before
that path. This is a concrete link baseline, not a working native cat. Next supply
truthful process-local mask state, private stdio transport and a reviewed terminal
seam before claiming startup/copy/finalization on the real Toybox image.

## Real native startup and private process mask

The [startup probe](evidence/toybox-native-mask-2026-09-07/README.md) now invokes
unmodified toy_singleinit on the actual cat descriptor after AECAT001 and copied
cat/LC_ALL=C validation. Private single-thread mask state starts0077; real umask
calls exchange0/0077 and restore0077, with old values0077/0. High requested bits
are masked off; uninitialized/retired state rejects. This is an opt-in probe-local
policy proposal, not a new syscall or file-creation permission implementation.

A real TLS sentinel is observed before/after startup. Existing native-memory
support is selected explicitly without changing limits; lack of its grant rejects
before Toybox. Wrappers call the real xmalloc and setvbuf, observing a4096-byte
buffer successfully installed on stdout. Real locale setup yields UTF-8. The probe
stops before cat_main and before Toybox callback/flush/exit adaptation, closes all
three bindings and lets the existing owner verify empty sinks and four reclaims.
Wrong-old-mask and skipped-init produce115/owner1501; missing memory grant produces
116/owner1501. Missing or stubbed initialization cannot satisfy these checks.

Reproduce with `python3 docs/evidence/toybox-native-mask-2026-09-07/run-native.py`.
It verifies retained link-audit inputs, rebuilds upstream main with symbol rename
only, links the scoped probe and uses the source-matched qualified empty-cat owner/
backend envelope. Upstream headers are system includes; original probe warnings
remain strict. Full prior command and connection/inherited regressions remain
selected. Allocation failure, locale fallback, actual copy/stdio/terminal integration
and independent CAT consumer acceptance remain open.

## Private native vector prerequisite

`user/native-command/vector-write.h` gathers at most two borrowed spans into a
16-byte request to the existing scoped transport. It is a private helper, not
an installed writev syscall or musl stdio replacement. Its caller supplies valid,
stable readable objects synchronously; FD1/2, vector counts, null spans and signed
aggregate overflow are checked before copying. Existing bindings still enforce
rights, generation and liveness. Short positive counts are confirmed progress;
EIO/EINTR stop the caller, and shared transport poison forbids later diagnostic
traffic. Nonempty zero progress maps to EIO. Cleanup retires all local aliases.

```sh
python3 docs/evidence/native-vector-2026-09-07/run-native.py
```

The [bounded experiment](evidence/native-vector-2026-09-07/README.md) substitutes
only the native client in retained owner envelopes, preserving independent byte,
position, terminal and reclamation checks. This does not execute actual musl's
stdio callback, Toybox cat_main or callback/flush/terminal adaptation.

## Actual native musl callback prerequisite

The opt-in `stdio-probe.c` runs musl1.2.6's actual internal __stdio_write loop
against the private vector bridge. The retained recipe verifies/extracts upstream
source, renames the callback and replaces only its writev syscall call. The real
FILE layout and valid disjoint buffers remain private to this single-thread probe.
Public headers must precede internal syscall macros, and musl's private include
wrappers precede the installed SDK headers. Upstream system-header treatment and
scoped sign-compare suppression apply only to the upstream callback; original C
keeps strict warnings. No installed libc or kernel interface is changed.

```sh
python3 docs/evidence/native-stdio-2026-09-07/run-native.py
```

The [experiment](evidence/native-stdio-2026-09-07/README.md) checks17-byte prefix
plus15-byte new data over16-byte messages, native short writes, zero-length output,
FILE reset/clearing, and eight confirmed new bytes before real EIO/EINTR. Unknown
write completion forbids any subsequent diagnostic channel traffic. A local
zero-progress injection checks finite EIO handling separately from native backend
behavior. This directly invokes the internal callback, not public fwrite/fflush,
Toybox cat_main or callbacks/finalization. These remain separate integration work.

## Public native stdio prerequisite

`public-stdio-probe.c` uses real SDK setvbuf/fwrite/fprintf/fflush/ferror, without
accessing private FILE fields. A private image supplies the upstream __stdio_write
symbol with only its writev call replaced by the scoped bridge; the installed SDK
archive remains unchanged. The original probe uses public SDK headers and
-fno-builtin so fprintf/fwrite calls remain actual library calls. Caller-owned
stdout buffering is selected before first stream use and stays live through final
fflush(NULL), before the three scalar alias closes. Stdin uses scalar read.

```sh
python3 docs/evidence/native-public-stdio-2026-09-07/run-native.py
```

The [experiment](evidence/native-public-stdio-2026-09-07/README.md) observes the first
17 bytes buffered without channel calls; the next 15 bytes overflow the effective
24-byte buffer and invoke the real write loop. Independent Rust owners check exact
binary output and stderr D/newline or usage64. Buffered fwrite acceptance does not
imply successful output: real EIO/EINTR/uncertain flushes retain ferror and the
expected status, and later diagnostic attempts after poison make no channel calls.
No automatic retry, heap allocation, global syscall allocation or kernel change.

This does not run Toybox, its xexit callbacks or a general libc finalizer. The
private image substitution is not an installed SDK API or consumer acceptance.
The existing plain ASCII usage/diagnostic bytes and boot markers remain unchanged;
no presentation adoption or new renderer conformance is claimed.

## Actual native Toybox cat and normal exit

The opt-in `toybox-cat-probe.c` composes actual startup (mask, TLS, locale and
allocator checks), unmodified cat_main/loopfiles/xwrite, and real Toybox xexit.
Two allocated fixture callback nodes demonstrate reverse order/signal0; actual
xexit pops and frees them. Link wrappers observe and call real fflush/ferror.
These names are taken from undefined object symbols, not disassembly alias labels.

```sh
python3 docs/evidence/toybox-native-cat-2026-09-07/run-native.py
```

The [experiment](evidence/toybox-native-cat-2026-09-07/README.md) patches only the
normal `_exit` argument inside _xexit to call a private cleanup hook. Its rebound
branch and separate vfork exit remain untouched. The hook checks callback/flush/
ferror ordering before locally consuming the three stream aliases. It preserves
prior nonzero status or promotes successful status on close error. This is a
single synchronous normal-exit witness, not a general recursive/signal finalizer.
Callback function/data-pointer conversion follows Toybox's existing x86_64 ABI;
functions remain live and callback nodes are exclusively owned by xexit.

Binary, empty and short no-argument stdin copies use independent existing owners.
Actual applet error diagnostics and unknown behavior require separately reviewed
owners matching Toybox's real request sizes and output bytes; the conformance
client's eleven-byte fault points must not be treated as those applet contracts.
Options/files remain outside this probe. Independent CAT acceptance and R1 remain
open; no installed SDK, kernel ABI or sibling changes are made by the private link.

## Actual Toybox I/O error profile

The retained owner recipe selects `--cfg toybox_applet` on the existing cat-role
owner. This keeps the default eleven-byte conformance profile and introduces
sixteen-byte fault/prefix accounting only for this opt-in image. A known error
permits subsequent stderr writes, never another input/output attempt. Exact
Toybox/musl diagnostic bytes and positions remain independently checked; unknown
completion permits no further channel traffic. Existing rights, generation,
terminal, local/remote closure and reclaim checks are preserved.

```sh
python3 docs/evidence/toybox-native-errors-2026-09-07/run-native.py
```

The [experiment](evidence/toybox-native-errors-2026-09-07/README.md) runs actual
cat read/write EIO/EINTR and malformed/cut reply paths. Read error leaves16 input
and output bytes; write error leaves32 input/16 output. First unknown read consumes
16 input/no output; first unknown write consumes16 input/output. Known errors emit
exact `cat: -: ...` or `cat: xwrite: ...` diagnostics and status1. A client counter
assertion covers all channel calls from poison through local retirement, including
upstream diagnostic attempts. Existing startup/xexit adaptation is reused.

This is not the applet's usage/options or recursive/signal-finalizer acceptance.
The diagnostic bytes are upstream ASCII output under the selected locale; no new
presentation format, kernel ABI, installed SDK or sibling change is introduced.

## Toybox-image profile usage gate

The cat image now rejects extra arguments after copied-startup/AECAT001 validation
and before toy_singleinit. Any extra argument (including -, empty, --help and
--version) gets the established `cat: this profile accepts stdin only` line and
status64. This is the private profile's bounded rejection, not upstream option/help
support. The no-argument path still runs the qualified actual applet.

```sh
python3 docs/evidence/toybox-native-usage-2026-09-07/run-native.py
```

The [experiment](evidence/toybox-native-usage-2026-09-07/README.md) uses real musl
fprintf/fflush on the diagnostic binding, consumes all aliases and preserves64
through known EIO/EINTR or unknown completion. Independent owners require zero
stdin requests/stdout bytes, exact diagnostic prefixes, native terminal/cleanup
and four reclaims. Assertions require no mask/Toybox allocator/callback state;
rejection also runs without a memory grant. No separate kernel/profile API is added.

This early path deliberately does not call Toybox's uninitialized exit machinery.
General finalizer errors/re-entry and independent CAT handoff acceptance remain
separate. Existing ASCII diagnostic bytes and stream roles are unchanged.


## Buffered callback finalization witness

The opt-in APP_FINAL_BUFFER mode reads the fixed32-byte binary input, then actual
Toybox xexit callbacks fwrite two ordered halves into its real stdout buffer.
Assertions prohibit callback channel traffic; actual xexit flushes before cleanup.
This isolates finalization and does not execute cat_main in that mode. The default
cat applet and usage modes remain separate regression requirements.

```sh
python3 docs/evidence/toybox-native-finalize-2026-09-07/run-native.py
```

The probe records fflush's return and validates upstream's conditional ferror call:
a failed flush skips ferror. Known flush errors emit exact upstream write diagnostics
only when prior status is zero;64 remains64 without another diagnostic. Unknown
completion suppresses transport calls, and cleanup consumes local aliases before
independent remote cleanup. Close failures promote0 to1 and preserve prior64.
Opt-in owner flags toybox_finalizer/toybox_final_status account for the full32 input
bytes and independently check output/diagnostics/status. Default owner modes retain
their existing contracts. The private cleanup hook rejects re-entry120 without
additional channel effects; recursive xexit and signal handling remain unqualified.
See the [contract and evidence](evidence/toybox-native-finalize-2026-09-07/README.md).


## Candidate final close policy

APP_CLOSE_POLICY selects the reviewed bounded cleanup behavior after actual
cat_main and xexit: close input/output, attempt one `cat: close failed` ASCII line
on still-live stderr for either failure, flush stderr, then close it. Any failure
promotes0 to1 and preserves64. Unknown completion forbids subsequent channel traps;
local retirement remains separate from owner-observed remote cleanup. There is no
fallback sink after stderr close. A nested private cleanup-hook call returns120,
latches failure without effects, and makes the outer cleanup nonzero after it
consumes the remaining aliases. Arbitrary recursive xexit/signals remain unsupported.
Older evidence modes are retained as separate opt-in profiles; consumer adoption
of this candidate is not implied by its implementation.

```sh
python3 docs/evidence/toybox-native-close-2026-09-07/run-native.py
```

The [contract](evidence/toybox-native-close-2026-09-07/README.md) selects actual cat,
each unknown close, failed final diagnostic and re-entry terminal controls. Owner
checks require input/output retired before diagnostic writes, exact bytes/prefix,
no traffic after uncertainty, distinct local/remote state and two-generation reuse.
