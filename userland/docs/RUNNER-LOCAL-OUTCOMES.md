# Proposed runner local-outcome handoff (UL-059)

2026-09-06. Ready for affected-owner review; not sent, accepted, implemented or a
shared standard. Aether owns the command-I/O broker/backend and native mechanisms;
userland owns parsing, presentation and independent consumer tests. The central
[contract catalog](../../../Aether-standards/docs/CATALOG.md) preserves domain ownership.
New shared requirements would use the standards contribution/versioning process.
This document requests a bounded domain extension without allocating wire fields,
descriptor numbers, authority or a new default pin.

## Current evidence and the concrete gap

The [consolidated owner review packet](RUNNER-OWNER-HANDOFF.md) supplies current
consumer evidence, owner decisions and the required return bundle. The latest
consumer run passes66 combined native cases and nine legacy cases; host delivery
and frontend results remain separate from native local-outcome acceptance.
Current command contract/owner/supervisor/backend hashes match the consumed
producer. Native local outcomes are waiting on the reviewed owner extension;
no sibling backlog entry or message was created here.

The mapped gate requires admission, child termination and consumed collection.
The release verifier expects `6\n` or `0\n`, and the output file has 64-byte capacity.
The parent receives two bindings (3/read and 4/read-write) and has no stderr grant.
Thus even a correct local exit is rejected, and changing only the parent status
comparison cannot qualify help or diagnostics. Existing positive child verification
and the finite exit29 suite must remain intact.

## Requested owner work

1. Add a separately selected experimental local-outcome profile and export a new
   source/evidence bundle. Keep existing ABI/wire bytes and all old pins immutable;
   the owner chooses the explicit compatible extension/version where additional
   roles or lifecycle observations need representation. Userland will rebuild its
   own clients against its pinned SDK and independently adopt the new bundle.
2. Supply explicit, separate runner stdout and stderr sinks with known bounded
   capacities: propose at least 512 stdout bytes and 256 stderr bytes for these
   fixtures. The roles confer only their specified write/close authority; do not
   derive them from FD numbers, names, UID or ambient console access. Preserve the
   existing child-I/O mapping. Owner review must decide the role/binding carrier,
   lifetime and validation rules before consumer implementation. Do not silently
   widen the current 32-byte two-binding bootstrap or map diagnostics to child stdout.
3. Independently observe launch requests, successful admissions, allocated child
   state and collection attempts for this invocation. For local actions, require
   zero launch requests, zero admissions and zero collections. For a complete
   denied admission, require the specified request/error and zero admissions;
   do not infer this from parent exit2 or a missing child terminal record.
4. Verify both sinks by backend readback: exact bytes and length, stream separation,
   and preserved input bytes/position for actions that perform no child I/O.
   Parent EOF is insufficient. Support expected-empty output and expected-prefix
   output for injected delivery failure without relaxing completed-child checks.
5. Independently verify every opened alias/backend handle and native instance is
   released or explicitly unresolved. A local run has parent/backend, no child:
   do not reuse the six-reclaim child oracle. If the same two-generation setup is
   retained, four native reclaims are the proposed expected total, subject to
   owner confirmation of its actual object set. Check per-generation identities,
   baseline-relative allocation effects and cross-generation independence.
6. Distinguish an expected operational-failure witness from successful delivery.
   Do not accept arbitrary early exits1/2/64. Bind each case to trusted initial
   input, independently observed effects, exact parent kind/status and lifecycle
   evidence. A broken parent that silently skips output or launches unexpectedly
   must fail the verifier even if its numeric status matches.

The first implementation may qualify a harness-only empty-output lifecycle before
adding streams. That must stay a prerequisite witness: it cannot complete the
Experience requirement that usage errors reach stderr or help reaches stdout.
Missing required sink authority is a launcher/profile precondition, observed before
publishing runnable startup; define how the owning launcher reports that failure.
No successful diagnostic no-op or newly fabricated stderr capability is acceptable.

## Proposed userland text and behavior

The inert [text fixtures](proposals/runner-local/) are candidate exact outputs;
version0.1 is a proposal for the experiment, not a released version assertion.
[Fixture identities](proposals/runner-local/manifest.json) record measured bytes
and line widths. Text is ASCII with LF, no styling, cursor control, user-input echo
or advertised unsupported flags. It fits 40-column presentation. Exact native
write/close, stream and accessibility acceptance are still NOT RUN.

Sole --help and --version use stdout and exit0 only after complete delivery and
required cleanup. Invalid invocation uses stderr and exit64 after successful
diagnostic delivery/cleanup. A complete owner rejection for absent name (ENOENT),
authority (EACCES) or capacity (EBUSY) uses its specific stderr fixture and exit2.
Keep exact wire error and no-admission evidence separate from the public number.
Malformed request/EINVAL is not automatically a public precondition outcome.
This proposal does not classify every possible errno or redefine child exits.

Any required delivery or cleanup failure produces operational exit1, retaining
the original action/error and what delivery/cleanup is known. Positive short writes
continue only with the unwritten suffix; zero/fatal writes fail. Ambiguous transfer
poisons without replay. Output capacity must not imply truncation success. Output
and diagnostic buffers cannot overwrite each other, and every owned close consumes
once. Details of unknown remote cleanup remain outside local-success acceptance.

## Acceptance cases for owner and consumer

All native RL cases below are NOT RUN; the later host checkpoint does not close them. Observe actual parent/child/backend facts; no
preconfigured expected status is proof by itself. Both owners retain independent
positive and deliberately broken cases under fresh source/SDK/artifact identities.

| ID | Input or injected condition | Required witness |
| --- | --- | --- |
| RL-01 | Sole --help / --version | Exact respective stdout, empty stderr, exit0; no launch/collection, complete cleanup |
| RL-02 | Missing command, unknown leading option, extra help argument, empty command | Exact usage stderr, empty stdout, exit64; no launch/collection |
| RL-03 | Valid absent command name | One complete rejected launch, ENOENT, zero admissions; unavailable stderr, exit2 |
| RL-04 | Denied command authority | Exact owner EACCES with zero admissions/unauthorized effects; denied stderr, exit2 |
| RL-05 | Capacity unavailable for this invocation | Exact EBUSY, zero admissions, partial reservation cleanup relative to baseline; capacity stderr, exit2; account for finite generation consumption |
| RL-06 | All-positive short writes | Exact complete bytes without duplication, correct0/2/64 and cleanup |
| RL-07 | Output capacity/exhaustion, zero/fatal write, diagnostic delivery failure | Exact observed prefix/empty opposite sink, exit1, original action/error retained; no launch replay |
| RL-08 | Required close report failure | Original action and delivery facts retained, exit1; distinguish known local failure from unknown remote release |
| RL-09 | Absent/wrong/duplicate sink role or stale generation | Startup publication/authority denied with no local I/O/child effects; exact launcher-owned outcome |
| RL-10 | Broken parent skips output, changes a byte, writes wrong sink or admits a child on --help | Independent verifier rejects each, even with expected numeric exit |
| RL-11 | Parent exits early, skips close, or reuses a prior generation result | Cannot falsely pass delivery/cleanup; owner records actual resources and rejects stale evidence |
| RL-12 | Existing finite, startup and mapped-child profiles | Preserve old terminal markers, exact byte verification and their separate cleanup counts |

A quota-control helper or pre-existing capacity consumer is outside the invocation's
child count and must still be explicitly accounted for in the fixture's baseline
and cleanup. Absence of a command child is not absence of all native objects.
The owner chooses and documents exact marker/context additions; old machine records
are preserved. Expected failure tests may pass their test oracle while the target
operation remains failed, and those two results must be recorded separately.

## Review decisions and next steps

Aether review must resolve the sink-role transport/version, capacities and exact
reclaim/object set, trusted local-case verifier input and missing-sink observation.
Userland review must approve final text/version, diagnostic-failure precedence and
independent consumer cases. Current-task technical review only; owner acceptance
and independent technical/reader walkthroughs are pending. No kernel backlog item,
message or review approval was created by this document.

Lost/truncated admission or collection is not zero admission. Keep the known
receipt if any and retain unknown-resource ownership; no retries, fake child death
or passing reclaim result may replace owner-defined resolution. General stop,
unknown recovery and package/sys-init activation remain separate follow-ons.

The previously planned mapped uncertainty, pending-budget and host local frontend
work now has scoped evidence below. Next native work is the owner extension in
[the review packet](RUNNER-OWNER-HANDOFF.md); further host tests cannot establish
missing native output authority or lifecycle acceptance.

## Host local-output delivery checkpoint — 2026-09-06

[Host-only delivery candidate](evidence/runner-local-delivery-2026-09-06/summary.json)
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
[local candidate guide](../experiments/command-runner/LOCAL-OUTPUT.md).
Next: host parser/admission-to-fixture delivery integration. Native use still needs
the proposed owner sink-role/lifecycle extension. UL-059 active; UL-069 deferred.

## Host local frontend checkpoint — 2026-09-06

[Host frontend evidence](evidence/runner-local-frontend-2026-09-06/summary.json)
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
