# Command-runner source review (UL-063)

2026-09-06. Technical review by the current Codex task; independent technical and
reader review remain pending. Scope is experiments/command-runner: runner,
two-binding native adapter, entry, bytecount, injected controls and three Python
build/test drivers. This is not a whole-repository security or conformance audit.

## Mechanical migration completed

Six C/header files now use pinned Clang-format 21.1.8 with the local style. Before
sources and initial dry-run failures are retained. No C edition, compiler flags,
protocol, marker or logic changed. All five rebuilt native client ELFs match the
UL-057 baseline byte for byte. The ten host cases, eleven injected controls and
native object inspection pass; formatting check passes. This supports retaining
prior scoped native behavior evidence, not a new native boot or public CLI claim.

[Evidence](../evidence/command-source-review-2026-09-06/summary.json) contains the
source snapshots, tool/style identities, exact binary comparisons and raw checks.
Python remains mechanically unchanged so its behavior corrections can be reviewed
separately. C11 compile profiles remain explicit historical profiles; migrate to
C17 in a separately tested change, not hidden inside formatting.

## Findings and required follow-ups

| ID | Finding and practical boundary | Required work before relevant behavior |
| --- | --- | --- |
| CSR-01 | prepare-native.py, native.py and check.py use subprocess.run timeouts without owning child process groups. Compiler/build descendants can outlive the direct child. Exceptions can bypass per-command evidence writes. | Add a bounded owned process-group runner, preserve timeout/start/cleanup failures, exercise a descendant-holding-output control and confirm no surviving process. Do not call present timeouts complete cleanup. |
| CSR-02 | Build drivers inherit host environment; some omit cwd. native.py resolves Zig/QEMU through PATH and records versions but not their resolved executable hashes here. | Explicit command-specific cwd/environment/tool resolution; retain exact helper identity and SDK/boot dependency verification. Test misleading PATH/compiler environment without consuming alternate tools. |
| CSR-03 | Existing native C edition is C11; dense Python top-level programs and positional source lists hinder review. Dead scenario branches survive in native.py (small-pool/parent-first/reserved/bad-third-machine are not in its nine-case list). | Separate readability/edition migration from behavior. Preserve exact test inventory; remove stale branches only with review and regression evidence. |
| CSR-04 | Adapter owns one connection and exactly two bindings, with fixed receipt prefixes/generations and bounded buffers. Bootstrap validates the pair before live publication, but dedicated malformed-pair/partial-transfer/re-entry controls are absent. | UL-058 must exercise atomic publication and poison/no-replay boundaries. Failed bootstrap leaves transport fields assigned, preventing retry; public lifecycle behavior must be explicit, not guessed from finite entry exit 120. |
| CSR-05 | Runner admission and collection are fixture assertions, not reusable public result decoding. send() checks padding, but callers impose their own exact expected errors/receipt. Poll limit maps to fixture assertion 53. | Implement UL-059 only after owner-approved startup/result/recovery contract and audited decoding; don't reuse assertions as public exit semantics. |
| CSR-06 | File adapter validates pointer nullness and up to 16 bytes, not arbitrary pointer mappings; memcpy can fault on non-null invalid memory. Mutable globals are single-thread only. | Preserve bounded trusted-caller scope; do not claim bad-pointer isolation or concurrency safety. Separate native witnesses if widening those domains. |

CSR-01/02 are blocking tooling corrections for new public-runner runtime work,
not findings that the already completed native cases failed. No timeout leakage
was deliberately exercised in this mechanical slice. CSR-04/05 are explicit
coverage/contract gaps, not demonstrated authority bypasses. No security defect
is waived by classifying a gap; keep missing tests visibly incomplete.

## Reviewed invariants

The adapter publishes both live entries only after the full bootstrap reply checks;
uses no local file positions; checks local descriptor rights/count; bounds transfers;
validates reply metadata/padding before caller-data copy; poisons transport on failed
transfer/malformed reply; consumes close locally once. Its errno wrapper preserves
the caller's errno for musl to interpret the returned result. Known close failure
is not retried. These are source observations plus prior scoped evidence, not
coverage of every partial/unknown outcome.

Bytecount has no transport or fixture data. It handles short I/O, rejects overlong
results/zero writes/overflow and closes descriptors once. EINTR retry is explicitly
command behavior; it does not add native signal support. Help/version capacity
and absent stderr remain distinct from success in the 64-byte native workload.

## UL-059 producer handoff review

Current Aether command-I/O documentation has more producer failure/fault coverage
than userland's pinned nine-case bundle; that does not automatically update this
consumer. Its conformance parent still has fixed startup and exit 29. Userland's
proposed CLI needs an opt-in producer profile carrying up to six parent strings,
actual child argv/env and mapped public result, while preserving the old mode.
The [public contract](../AETHER-RUN.md) names AR-01–14 acceptance and owner roles.

Package reconstruction remains inert and must consume matching artifacts. Current
sys-init runtime model evidence is synthetic service-policy work and does not
establish this public native result mapping. No source/receipt change, sibling
edit, message or owner sign-off occurs through this review. Unknown-outcome
resolution and resource ownership need a concrete producer agreement; CLI exit 1
alone cannot resolve an admitted child. Shared protocol decisions remain in
Aether-standards. UL-059 and UL-063 remain active.

Next: correct CSR-01/02 in a dedicated tooling change with failure controls;
then complete the remaining scoped review and UL-058/native acceptance work.

## CSR-01/02 correction checkpoint — 2026-09-06

The three drivers now use process.py with explicit cwd/environment, absolute
executables, per-command tool identity and retained start/timeout/exit/cleanup
records. Commands own a new process group; timeout or remaining descendants
trigger group kill, direct-child reap and bounded group-disappearance checks.
A leader exiting while a descendant remains cannot pass. Detached sessions are
outside this helper's contract; no general daemon cleanup claim is made.

Seven process/environment controls pass, including live grandchild timeout,
early leader exit, missing tool, normal/nonzero status and hostile environment.
An actual 21-case host build passes from a foreign cwd with hostile PATH, CC,
CPATH and CFLAGS. All five client ELFs remain byte-identical to the baseline.
Nine native cases pass using the same producer pin and smoke expectations.

Native Zig, Rust, rust-lld/toolchain dylibs, QEMU and xorriso are hash-pinned in
host-tools.lock.json. A private rustc wrapper supplies only the verified Rust
library directory to nested Rust commands; Zig/QEMU do not inherit it. Four
failed attempts discovered the missing Rust path, cross-tool LLVM collision,
nested Rust invocation and xorriso dependency; all retained. The successful native
run executes the unmodified owner smoke module inside an owned Python subprocess.
Producer boot-dependency checks and old markers remain unchanged.

Default per-file bound is 16 MiB; native build commands declare 512 MiB for image
artifacts. These are file bounds, not total disk/memory/flood guarantees. Captured
logs and input bytes live in each private build root. Ordinary nonzero exits are
recorded with completed cleanup; callers separately require their expected status.
Tool hash identity does not authenticate every transitive host library or establish
bit-reproducible kernel images. Existing tool/SDK provenance limits remain.

[Evidence](../evidence/command-tooling-2026-09-06/summary.json) supports marking
CSR-01/02 corrected for these three drivers. CSR-03 readability/C17 migration,
CSR-04/05 native boundary and public contract work, and independent review remain.
UL-063 and UL-059 stay active. Earlier findings are historical audit context.

## CSR-03 edition and stale-scenario checkpoint — 2026-09-06

Host/object and five-client builds now select C17 with the existing pinned LLVM
and diagnostics. Source-pinned producer helper/adapter C retains C11. Four
unreachable scenario branches were removed from native.py; its exact nine-case
inventory, markers and terminal order remain unchanged. Twenty-one host/control
cases and all nine native cases pass; all five client ELFs are byte-identical to
the retained C11 baseline. No C source or protocol change occurred.

[Evidence](../evidence/command-c17-2026-09-06/summary.json) retains before/after
drivers, the reviewed diff, build results, native logs and cleanup receipts.
CSR-03 still requires readable Python entry points and named source references.
Independent technical/reader review and CSR-04/05 remain open; UL-063/059 active.

## CSR-03 Python restructuring checkpoint — 2026-09-06

All three drivers now enter through main(), with import-time builds/argument
parsing removed, expanded statements and command arguments, named runner/channel
sources and pure native expectation helpers. Normalized execution AST review
finds only these declared changes; eighteen helper comparisons preserve the old
nine-case contexts and terminal sequences. Host/client/native command argv and
exits match the C17 baseline after private root normalization. Twenty-one
host/control cases, seven process controls and nine native cases pass; five client
ELFs are identical. No C behavior, flags, wire protocol or pin changed.

[Evidence](../evidence/command-readability-2026-09-06/summary.json) retains the
review scripts, before/after sources and raw tests. This completes the scoped
CSR-03 entry-point/named-source restructuring. Some long expressions and generated
code strings remain beyond the CP line target; no full PEP 8 lint claim. Current
task technical review is recorded; independent technical/reader review remains
pending. UL-063 remains active for these reviews and broader migration. CSR-04/05
are the next boundary/contract work through UL-058/059, not silently waived gaps.

## Producer refresh and boundary design — 2026-09-06

The [new integration review](../RUNNER-INTEGRATION.md) supersedes the historical
missing-carrier/mapped-result dependency: a verified 293-file producer bundle
provides both in an opt-in profile. Existing consumer pins and native evidence
remain unchanged. Zero-admission/help/error and unknown recovery are not accepted
by its admitted/collected result gate. Independent consumer work remains.

[UL-058 design](../../experiments/command-runner/BOUNDARY-PLAN.md) specifies 14 host
groups/four native follow-ons, NOT RUN. Source review flags a failed-bootstrap
poison/retry concern for CB-07; it is not yet a demonstrated native exploit or a
waived condition. Independent reviews remain pending.

## CSR-04 bootstrap correction — 2026-09-06

[UL-058 host controls](../evidence/command-bootstrap-2026-09-06/summary.json)
confirm the failed-initialization retry/traffic defect (13 original failures).
One-attempt initialization with common poison-on-failure fixes those paths while
preserving atomic publication and successful re-entry. Twenty-two UBSan scenarios
and two exact mutation controls pass; 21 host and nine native legacy regressions
pass with five freshly inspected changed ELFs. Native bootstrap failure injection
and remaining transport cases are still open. ASan is incomplete on the current
host (empty-main timeout); UBSan selection is explicit. Independent reviews pending.

## CSR-04 host reply/transfer coverage — 2026-09-06

[53 host scenarios and two mutations](../evidence/command-transfer-2026-09-06/summary.json)
now cover short/failed transport, exact retry budgets, malformed/lost read/close
replies, signed error bounds and no replay after poison. All 24 bootstrap and
21 host command regressions pass; adapter source is unchanged. The first validator
mutation failed compilation and was not counted; corrected semantic rejection is
retained. Native NB-01–04, ASan support and independent reviews remain open.

## CSR-04 native bootstrap witness — 2026-09-06

[NB-01 evidence](../evidence/native-bootstrap-userland-2026-09-06/summary.json)
adds real musl/no-traffic verification for three corrupt second-binding fields,
and detects early publication at an exact distinct child exit. Thirteen cases
pass with the explicitly selected new producer; nine original-pin regressions and
21 host cases pass. Normal adapter unchanged; five legacy client ELFs identical.
Remote recovery, NB-02–04, ASan and independent reviews remain incomplete.

## CSR-04 native reply witness — 2026-09-06

[NB-02](../evidence/native-replies-userland-2026-09-06/summary.json) verifies lost/
malformed read and lost close after actual replies. Three controls require
child 84 after errno/sentinel/no-traffic checks; disabled poison is caught at 94.
Parent 53/broker970 are deliberate rejection, not recovery. All 17 combined native,
nine original and 21 host regressions pass; adapter and prior nine ELFs unchanged.
NB-03/04, ASan and independent reviews remain open.

## CSR-04 native launch framing — 2026-09-06

[NB-03](../evidence/native-launch-userland-2026-09-06/summary.json) adds exact
complete-frame errno/zero-receipt and aligned follow-on, seven truncated prefixes
with no terminal records, and two semantic broken-producer controls. All 27
combined, nine original and 21 host cases pass. Thirteen prior ELF bytes remain
unchanged. EOF containment is not recovery; NB-04/public CLI and reviews remain.

## CSR-04 terminal witness and next public boundary — 2026-09-06

[NB-04](../evidence/native-terminal-userland-2026-09-06/summary.json) distinguishes
actual fault from equal-number normal exit, retains one-time collection and six
reclaims, and detects misreported kind. All 30 combined, nine original and 21 host
cases pass; twenty-one earlier ELF bytes unchanged. Scoped NB-01–04 now have
witnesses. CSR-05 public decoding/startup, independent review and broader recovery
remain open; finite parent29 is not public result mapping.


## CSR-05 pure startup decoding — 2026-09-06

[Parser controls](../evidence/runner-parser-2026-09-06/summary.json) pass 1,293
UBSan assertions and two exact semantic mutations. Decode validates complete
carrier bytes before copying to the caller; selection revalidates typed input
before fixed-capacity argument/environment publication. Every non-launch action
leaves invocation storage unchanged, requiring explicit caller action dispatch.
Current-task technical review checked bounds, short-circuit ordering before string
operations, private lifetimes and no implicit transport/authority. Inputs must
remain live and disjoint; this is not arbitrary pointer validation or concurrency
support. Strict C17 diagnostics and native object imports pass; existing 21 host
regressions pass. Independent technical/reader reviews remain pending. Public
result decoding, native startup observation and owner acceptance remain open.


## CSR-05 native startup wiring — 2026-09-06

[Startup evidence](../evidence/runner-startup-2026-09-06/summary.json) adds one
opt-in initialization owner with private carrier decode and pair validation
before publication. Current-task technical review checked that neither entry
retries consumption, all failing paths poison exchange, startup storage is owned,
and the selector alone chooses child slots. The native child observer independently
checks argc/argv and the complete environment, with a fourth-argument mutation
that rejects at exact child80/parent53/broker970. The finite parent retains29;
public result decoding and broader owner acceptance remain pending.

270 UBSan startup scenarios and two semantic mutations pass; the first retry
mutation on an already initialized transport was ineffective, so missing-aux
coverage was added and the initial result retained. Parser, 24 bootstrap, 55
transfer and 21 command regressions pass. All34 combined native and nine legacy
pass; prior25 client ELF identities unchanged. Strict new-C checks, format and
Python grammar pass. Independent technical/reader reviews remain pending.


## CSR-05 pure admission/collection results — 2026-09-06

[Result decoder](../evidence/runner-results-2026-09-06/summary.json) passes28,159
UBSan assertions and four semantic mutations. Current-task review checked complete
validation before publication, receipt context, zero error payloads, unsigned
wire parsing and bounded signed conversion. The policy preserves raw kind/detail
and requires explicit completed cleanup; host errno constants are not used for
wire identities. Invalid decode leaves output untouched; callers must dispatch on
the returned action. This stateless component cannot establish one-time collection,
authenticity or recovery. Strict C17 and native object inspection pass, with no
external imports. Parser and21 command host regressions pass. Independent reviews
and native mapped-result adoption remain open; ordinary runner/adapter unchanged.


## CSR-05 native collected-result mapping — 2026-09-06

[Mapped evidence](../evidence/runner-mapped-2026-09-06/summary.json) passes47 combined
and nine legacy native cases. Current-task technical review checked use of decoder
actions before receipt/terminal access, pending-only collection retries, bounded
unknown aborts, one-time parent closes and raw facts preserved through cleanup.
All normal selected statuses and actual fault map correctly; wrong-kind/forced-zero
controls reject. The close-error hook sees raw child0/kind1/receipt and false
cleanup before parent1/broker970 rejection. That is local report failure, not
remote close failure or recovery. The parent has musl read/close and no write import.

Prior28 client ELF identities match. The initial compile-only build included an
unnecessary bytecount object in mapped parents; it was removed before the passing
native run and retained with its exact sources. Strict mapped C checks, format,
Python grammar, result/parser and21 host regressions pass. Independent reviews,
zero-admission public outcomes and mapped-path uncertainty controls remain open.


## CSR-05 mapped uncertainty host control flow — 2026-09-06

[25 scenarios/four mutations](../evidence/runner-uncertainty-2026-09-06/summary.json)
pass on actual runner.c/mapped-runner.h plus real decoders. Current-task review
checked independent complete-frame expectations, fresh process state, strict I/O
ordering and callback guards. Lost/malformed replies forbid later effects; only
valid pending repeats, with success possible on the100,000th poll and exhaustion
otherwise. Raw terminal facts and cleanup reach the real policy through a witness.
Retry-lost, extra-poll, skipped-close and erased-detail mutants fail exact oracles.
Production source hashes match the prior native mapping run. Parser/result and21
host regressions pass; no new native execution or real resource-resolution claim.
Independent review and native mapped uncertainty controls remain pending.


## CSR-05 native mapped uncertainty — 2026-09-06

[Native controls](../evidence/runner-native-uncertainty-2026-09-06/summary.json)
pass five real-reply fault injections and one retry mutation. Current-task review
checked phase-specific interception, contiguous bounded fragments, original field
validation before injection, distinct runner1/witness101-or102/owner970 outcomes,
and the pre-adapter replay guard109. Child scheduling is not assumed for admission;
collection requires actual normal child0. Guarded calls cannot continue after the
injection. This is abort evidence, not complete cleanup or unknown-state recovery.

All 53 combined native, nine legacy and selected host regressions pass first attempt.
Prior42 client ELF identities remain unchanged. Strict new C, format, Python grammar
and quality checks pass. Independent reviews, native startup/pending follow-ons
and owner local-outcome adoption remain pending.

## Native startup rejection checkpoint — 2026-09-06

[Nine native controls](../evidence/runner-native-startup-2026-09-06/summary.json)
reject corrupted real carrier magic/count/reserved/slot padding, invalid second
binding rights, and receive prefixes0/223/255. Witness111 checks unpublished
arguments/references, real musl EBADF on FD0–4 and no auxiliary lookup/channel
activity on retries. A private early-argument-publication adapter mutation triggers
witness112 before the following receive. No child is launched. Exact parent-only
terminal records and owner970/990 with reclaimed0 establish deliberate rejection,
not cleanup or recovery. Original complete records are validated before mutation;
partial receives are local fault injection, not a remotely truncated producer.

All62 combined native cases and nine original-pin cases pass; all48 prior client
ELFs remain identical. Host startup270+2 mutations, mapped25+4, parser1293+2,
result28159+4 and21 command regressions pass. Source review corrected intermediate
pointer arithmetic in the new test witness; the superseded attempt and corrected
rerun are retained. Production code and producer/SDK pins are unchanged.
Native pending-budget controls, independent reviews and owner acceptance of local
help/error/output and unknown-resource recovery remain open. UL-059 stays active.

Current-task technical review checked fragment arithmetic/lifetime, complete-record
validation before mutation, unpublished binding/argument observations, bounded
single-attempt startup, real libc failure paths, private mutation linkage and exact
terminal/rejection oracles. Independent reviewer sign-off is still pending. The
new pointer correction is a test defect, not a discovered production adapter defect.
No native sanitizer, remote truncation or general malformed-input audit is claimed.

## Native collection-budget checkpoint — 2026-09-06

[Four native controls](../evidence/runner-native-budget-2026-09-06/summary.json)
exercise the unchanged 100,000-attempt runner bound. After obtaining an actual
child0/kind1 collected result, a private wrapper supplies local canonical pending
replies and counts synthetic yields without scheduling. Completion on the final
allowed attempt returns0, uses real EOF/closes and passes two generations with six
reclaims. Exhaustion returns1 with no further transport/output cleanup/policy
calls, verified by witness114. Private off-by-one mutants produce witness115 before
attempt100,001 reaches transport, or witness116 after only99,999 attempts. Negative
cases require exact child0/parent witness/owner970 with reclaimed0 and no success.

All 66 combined native cases, nine legacy cases and affected host regressions pass;
all 57 prior client ELFs remain identical. The first attempt passed. This is Aether
execution of runner control flow with injected replies/yield observation, not
100,000 remote pending exchanges, stuck-child scheduling, a time deadline or
unknown-resource recovery. Production behavior and all producer/SDK pins remain
unchanged. Current relevant owner contract/broker/backend hashes still match the
consumed producer; local help/error output needs the proposed owner extension.

Next local work: plan host local-outcome delivery and cleanup controls against the
proposed output fixtures. Native local outcomes, unknown-resource recovery and
independent reviews remain open. UL-059 stays active; UL-069 remains deferred.

## Host local-output delivery checkpoint — 2026-09-06

[Host-only delivery candidate](../evidence/runner-local-delivery-2026-09-06/summary.json)
passes 6,130 UBSan scenarios and four semantic mutations against the six pinned
proposal text fixtures. Positive short writes retain only the unwritten suffix;
known write failure still closes each owned logical sink once, while unknown or
malformed results stop all calls on the shared connection. The state preserves
original action/admission error, confirmed byte progress and individual close facts.
Exit0/2/64 requires complete delivery and both successful close reports; other
outcomes return1 without replay. Logical sink labels grant no native authority.

Parser/result/mapped and21 command host regressions pass. Both the initial algorithm
run and final contributor CLI adoption run are retained. Native behavior is unchanged
and not rerun here; native RL-01–12, remote resource recovery and independent reviews
remain open. This helper is not wired into runner.c or a package. See the
[local candidate guide](../../experiments/command-runner/LOCAL-OUTPUT.md).
Next: host parser/admission-to-fixture delivery integration. Native use still needs
the proposed owner sink-role/lifecycle extension. UL-059 active; UL-069 deferred.

## Host local frontend checkpoint — 2026-09-06

[Host frontend evidence](../evidence/runner-local-frontend-2026-09-06/summary.json)
connects the actual carrier/parser, admission decoder and local-output helper.
Help/version/usage select pinned generated fixture bytes without an admission
callback. Launch selection forwards the complete owned invocation once; only
validated complete ENOENT/EACCES/EBUSY replies select unavailable/denied/capacity.
Accepted admission returns a distinct receipt-bearing action, without local output
or collection. Unknown/malformed replies, unsupported errors and invalid startup
produce no invented diagnostic, replay or cleanup. Original parser/admission facts
remain separate from local delivery failure.

The 280 UBSan scenarios cover28 configurations, two generations and five delivery
modes (inert for nonlocal outcomes). Three mutations detect admission on help,
collapsed denial classification and repairing malformed reply padding. Existing
6130 delivery/four-mutant, parser/result/mapped and21 command host regressions pass.
The initial mutation-anchor setup failure and corrected passing rerun are retained.
No native production path changed or ran here; native RL-01–12 and independent
reviews remain open. Next: consolidate the affected-owner handoff with current
consumer evidence. Native local outcomes still need the proposed sink/lifecycle
extension and a new explicitly pinned producer bundle. UL-059 stays active.

## SI-07 affected source review and client build — 2026-10-03

Codex completed the affected UL-063 technical inspection before editing bootstrap,
role/result profile logic; [review and results](../evidence/sustained-runtime-2026-10-03/README.md)
record bounds, lifetimes, full-width conversion, atomic publication, poison/close
semantics and the unchanged finite runner/bytecount selection. Maintained opt-in
v2 clients now link;170 isolated transport cases,65535epoch peer sweep, role/result
controls and three semantic mutations pass the host gates. Legacy parent and
pre-change child rebuilds retain whole-ELF identity. Independent source/reader review,
native five-cycle/exhaustion/cleanup/halt acceptance and broader UL-063 remain open.

## Matched owner consumer checkpoint — 2026-10-03

[Independent replay and findings](../evidence/si07-consumer-2026-10-03/README.md)
verify complete producer/archive/source seals, ISO kernel/payload closure and nine
fresh native cases. Five cycles including3, seeded private-ID boundaries, exhaustion,
parent mismatch and cohort cleanup pass.242 ordered-trace counterexamples reject.
No new defect identified in inspected scope; no human reader approval is inferred.
Missing native child mismatch and broader malformed/stale/foreign/partial/close
schedules plus sys-init interruption policy prevent full SI-07 acceptance.
