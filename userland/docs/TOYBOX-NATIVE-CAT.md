# Bounded native cat candidate (UL-067)

## Consolidated local acceptance checkpoint — 2026-09-07

This matrix supersedes earlier NOT RUN/partial notes only for the exact scopes
below. UL-067 remains active; bounded cat qualification can proceed alongside
UL-007 native dash integration. Optional refinement stays deferred under PRF-01–03.

| Case family | Local evidence | Remaining acceptance boundary |
| --- | --- | --- |
| CAT-01 admission | Actual-applet positive admission; broader captured command-suite controls | Complete actual-applet admission matrix and independent review |
| CAT-02 copy | [7 copy/exit cases](evidence/toybox-native-consumer-2026-09-07/README.md), binary/empty/short input | Bounded workload only |
| CAT-03 usage | [20 cases](evidence/toybox-error-usage-consumer-2026-09-07/README.md), extra-argument rejection and diagnostic controls | Full malformed-bootstrap composition review |
| CAT-04 initialization | Real normal applet startup and selected allocation failure evidence | Full locale/allocator/stdio initialization denial matrix |
| CAT-05 I/O | [11 error cases](evidence/toybox-error-usage-consumer-2026-09-07/README.md), plus close-policy compositions | Selected finite streams, not general file/TTY support |
| CAT-06 finalization | [18 finalizer cases](evidence/toybox-finalizer-consumer-2026-09-07/README.md) and [27 close-policy cases](evidence/toybox-close-consumer-2026-09-07/README.md) | Named close-diagnostic/uncertain-close/re-entry gaps qualified; arbitrary recursive/signal exit unsupported; independent review pending |
| CAT-07 cleanup | Accepted outcomes check four reclaims; broader lifecycle controls in captured suite | Complete actual-applet abnormal-stop composition |
| CAT-08 regression | [213 current-revision local cases](evidence/toybox-close-regression-2026-09-07/README.md) plus 27 actual-applet close cases | Broad command regression qualified on current close snapshot; full matrix and independent review remain |

Backend payloads match [local source rebuilds](evidence/toybox-backend-rebuild-2026-09-07/README.md),
including the 27 close cases. These counts overlap and must not be summed as unique
coverage. Full matrix/revision review, UL-016 provenance/licenses and public package/
manual registration remain release gates. The restricted artifact is not general
/bin/cat. The next roadmap implementation seam is the
[native dash startup/process/FD sequence](NATIVE-DASH-GAPS.md#native-sdk-preflight-and-next-integration-ul-007).


Current checkpoint,2026-09-07: [local native execution](evidence/toybox-native-consumer-2026-09-07/README.md)
passes actual Toybox binary/empty/short copies and four exit-path controls using
captured sources and verified owner payloads. CAT-02 now has local evidence;
other rows remain partial or unqualified as recorded there. The proposal and
earlier NOT RUN/waiting text below are historical. Overall UL-067 is active,
not accepted. [Error/usage qualification](evidence/toybox-error-usage-consumer-2026-09-07/README.md)
now adds31 passing local cases for CAT-03/05. Finalization gaps, full producer
rebuild/regressions and independent review remain next.

[Finalizer qualification](evidence/toybox-finalizer-consumer-2026-09-07/README.md)
adds18 local cases and7 normal-copy regressions. CAT-06 remains partial; its
[remaining implementation proposal](../experiments/toybox-native/FINALIZATION-GAPS.md)
records close diagnostics, uncertain outcomes and repeat-entry terminal behavior.

[Close-policy qualification](evidence/toybox-close-consumer-2026-09-07/README.md)
now passes27 local cases addressing those specific CAT-06 gaps. This is bounded
candidate evidence; full matrix review and new-revision regression assessment
remain open. Next roadmap work returns to native dash launch/process/FD integration.

Proposed 2026-09-06; no native implementation or affected-owner acceptance.
This is a userland experiment plan, not a shared standard, package recipe or
public cat support declaration. Shared requirements remain in Aether-standards;
[the applicability map](DISTRIBUTION.md) and [quality process](quality/PROCESS.md)
apply. The [source and reference audit](research/TOYBOX-NATIVE-AUDIT.md) supplies
measured evidence; all native cases below are NOT RUN.

## Recommended first scope

Use the pinned Toybox0.8.14 standalone cat configuration and its upstream byte-copy
loop. First qualify exactly one argument, `argv[0] = "cat"`, no operands/options,
and the existing bounded `LC_ALL=C` environment selection. Input comes only from
an explicitly inherited readable stream; output and diagnostics require separately
validated writable roles. Propose finite input up to32 bytes and output capacity
at least32 bytes, including empty/binary input and multiple16-byte protocol turns.
These are initial verifier workload bounds, not silent truncation rules in cat.
Larger workloads need an explicit capacity/termination test profile.

The candidate adapter must reject all additional arguments before Toybox option
parsing or input consumption. That includes `-`, `-u`, formatting flags, filenames,
`--help`, `--version` and unknown options. Repeated stdin operands and public CLI
support can follow later. Such rejection is experimental adapter policy, not an
assertion about upstream cat's accepted syntax. Propose status64 and a fixed ASCII
stderr diagnostic, with exact reviewed bytes pinned before implementation. Do not
register this restricted artifact as a general `/bin/cat` package.

Keep stdout empty for rejected startup. If bootstrap authority is malformed, do
not publish any partial binding or attempt an invented emergency stderr write;
report the failure through the owner-observed terminal/lifecycle path. Missing
required authority must prevent Toybox startup. Names, argv and package hashes
never select or grant execution authority by themselves.

## Startup and termination ownership

The recommended integration preserves normal toy_singleinit and upstream cat
semantics. Do not set NOFORK, skip locale/allocation/umask initialization or replace
unsupported libc calls with successful stubs. No patch is selected by this plan.
A later reviewed adaptation needs its own source identity and regression evidence.

1. Native runtime validates the exact startup envelope and complete role set before
   publishing bindings. Userland validates the bounded invocation before calling
   Toybox. Reject unsupported startup without input reads or output writes.
2. Establish truthful process-local umask behavior and the selected musl locale,
   allocator, TLS and stdio closure. A process-local mask need not be a new kernel
   service, but its initial state, lifetime and future creation semantics need an
   owned contract. It never grants namespace or file authority. LC_ALL=C does not
   guarantee Toybox retains C character classification.
3. Run upstream startup and copy. Preserve short positive I/O counts. Current cat
   stops with an error on EINTR; do not claim bytecount's retry behavior applies.
   An ambiguous transport result poisons the connection; never replay a write or
   turn an unknown result into EOF. Any future retry policy requires its own review.
4. On normal/error termination, run Toybox's callbacks and upstream fflush/ferror
   handling while sinks are still live. Then invoke one reviewed finalization seam
   before terminal exit. Toybox may call _exit and never return to its caller;
   cleanup placed only after main is insufficient. Do not close stdout in a
   pre-flush callback. Fault/forced-stop cleanup remains owner-supervised.
5. The seam consumes each locally owned input/output binding once. Retain an
   existing nonzero command status; a close failure promotes a previously zero
   result to proposed status1. Keep diagnostic authority live until any final
   failure diagnostic is attempted, then consume that binding once. A diagnostic
   delivery/close failure cannot become a successful outcome. Record local close,
   remote acknowledgement and native reclaim as separate facts; do not retry an
   uncertain close or claim remote reclamation from local table state.
6. Report the resulting terminal outcome to the supervising owner. Independent
   backend verification checks exact output/prefix, input preservation, descriptor
   ownership and all required resource reclaim across generations. The candidate's
   reported status alone is not an acceptance oracle.

A review must decide the actual finalization hook, recursion protection, supported
stdio syscall closure and malformed-bootstrap terminal detail before target code.
No global musl `_exit` override or changed existing runner exit contract is implied.
The native-entry/bytecount finish path is useful comparison evidence, not reusable
Toybox cleanup without this composition work.

## Current gaps and domain owners

| Gap | Current reviewed boundary | Required next decision |
| --- | --- | --- |
| Executable admission | Aether command owner recognizes bytecount in a fixed launch frame | Aether selects an opt-in cat artifact/admission/verifier identity; preserve bytecount and current startup/mapped profiles |
| Child diagnostic authority | Current child bootstrap has stdin0/read and stdout1/write only | Aether owns role transport, versioning, grants and lifecycle. UL-059 requests runner-local outputs; acceptance of those does not automatically supply child stderr |
| Runtime initialization | Userland command facade only supplies bounded I/O; Toybox retains umask/locale/allocation/stdio | Userland audits exact native SDK call paths and proposes missing adaptation; Aether reviews any mechanism/authority change |
| Shutdown seam | native-entry calls bytecount_main; bytecount owns its finish closes | Userland proposes/test-drives one Toybox termination integration; owner qualifies effects and reclaim, including failed/unknown close |
| Verifier workload | Existing command backend is64 bytes and validates bytecount-specific positions/results | Aether reviews finite cat fixtures, exact output and failure prefixes, no-read rejection and lifecycle totals; do not merely change expected exit |
| Packaging/activation | This is a private experiment with pinned reference source, not a deployable package | pkg-mgr owns future recipe/trust/payload; sys-init owns lifecycle policy. Neither is implemented or accepted here |

Canonical domain routing is in the [standards catalog](../../../Aether-standards/docs/CATALOG.md).
Current owner contracts: [command I/O](../../aether/docs/NATIVE-COMMAND-IO.md),
[runner](../../aether/docs/NATIVE-COMMAND-RUNNER.md). Existing runner review packet:
[UL-059 handoff](RUNNER-OWNER-HANDOFF.md). This proposal adds no wire layout,
operation number, cross-project normative rule or competing owner backlog ID.

## Proposed native acceptance matrix

CAT-01–08 are local case labels under UL-067. Every row remains NOT RUN, including
rows with analogous Linux/host evidence. Preserve existing smoke markers and pins.

| Case | Required positive/negative witness |
| --- | --- |
| CAT-01: admission | Exact selected artifact and argv/env copied before admission; altered/unknown name, malformed strings and missing roles reject before publication; no authority derived from argv |
| CAT-02: copy | Empty, NUL/high-byte and32-byte inputs produce exact output once; authoritative input unchanged; forced short reads/writes cross multiple protocol turns |
| CAT-03: startup scope | Extra argument/options/filename reject with exact status/diagnostic, zero input reads and empty stdout; malformed bootstrap uses only the authorized terminal path |
| CAT-04: initialization | Observe real umask save/restore, locale success and denied fallback, allocator/stdio failure; no missing syscall hidden by a successful stub; bind tests to actual native SDK |
| CAT-05: I/O errors | Read/write failure and committed-prefix failure retain exact status/diagnostic/prefix; EINTR behavior explicitly observed; malformed/lost reply poisons with no replay |
| CAT-06: finalization | Callback/flush precedes sink close; exactly-once local consumption; positive and failed/unknown close, diagnostic failure and re-entry controls cannot produce success or duplicate effects |
| CAT-07: lifecycle | Two generations independently verify resource inventory and reclaim after normal exit, failed startup, command error and abnormal stop; no inherited alias leak or cross-generation use |
| CAT-08: regression | Existing bytecount/runner and legacy profiles pass against the selected producer, with unchanged prior artifacts where expected; deliberate skipped-copy, wrong-prefix and omitted-close mutants fail |

## Review handoff and local next action

The owner-facing request is ready locally: review an opt-in cat admission and child
stream/diagnostic profile, then return immutable contract/source/tool/SDK/artifact
and raw verifier evidence with exact resource inventory, failure attempts and
case status. The user-requested intake is now recorded in Aether UP-02/STATE; design review
and implementation remain pending. Do not silently pin
mutable owner work. Reuse the UL-059 return-bundle process without treating its
runner-local output scope as a child-role contract.

The [native SDK audit](research/TOYBOX-NATIVE-SDK.md) and
[combined reference fixture](../experiments/toybox-reference/COMPOSED.md) now cover
the local dependency/integration investigation. The consolidated
[owner packet](TOYBOX-OWNER-HANDOFF.md) records evidence, requested decisions and
return-bundle acceptance. Native UL-067 is waiting for reviewed producer inputs;
planning intake is recorded in Aether; native code/pins remain unchanged. Source authenticity, independent
review and packaging remain open. UL-059 waits on its separate runner-local bundle;
UL-069 remains deferred by the current work order.
