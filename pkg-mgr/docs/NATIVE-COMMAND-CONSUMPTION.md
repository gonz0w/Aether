# Package consumption: inherited libc and a useful command

2026-09-05. Package-owned acceptance preparation after UL-052. This records our
transport boundary and required consuming evidence, not an implemented native
workload or approval on behalf of another project. Shared requirements and
cross-owner agreement remain in Aether-standards. [Review input pins](evidence/inherited-libc-readiness-2026-09-05/review.json).

## UL-053 acceptance preparation (now consumed)

UL-052 completed the [inherited libc design review](../../userland/docs/INHERITED-LIBC-PLAN.md).
All 19 retained review-file hashes verify. It produced no executable or native
acceptance report. Userland can implement its selected workload using the already
accepted UL-051 broker; new kernel primitives are not required for this slice.

The old four-descriptor facade keeps local offsets. The inherited broker owns
positions and cross-client references, so the new adapter must keep one validated
binding with no local offset. Indices 3 and 10 are fixture bindings, not a newly
adopted general descriptor-table limit. This is a distinct consumer, even though
its expected artifact envelope remains AENMX001 / ABI 9.

Package integration will require a completed, externally pinned consumer report
and the exact accepted images, tool closure and independent outcomes. Do not add
a guessed schema, case names, status codes or an executable harness selector from
this prose. Use the owner's completed receipt to make those details concrete.

| Required consuming evidence | Package-side check once delivered |
| --- | --- |
| Actual musl read/close | Preserve separate probe/link-map and hook identities in producer evidence; boot exact accepted client bytes, not the older raw-RPC client |
| Broker-owned position | Exact ab/cd/ef reads after invalid, zero-length and unsupported-size calls; no hidden read-ahead or client offset repair |
| Narrow public API | Two-byte read, local zero-length handling, defined errno and explicit rejection of unsupported operations; no general C/stdio claim |
| Normal lifecycle | Both exit orders, rejected launch and partial reservation retry, six reclaims, file-close/result independence and one-time collection |
| Broker semantic controls | Preserve the five UL-051 rejection properties against the new libc clients, using their new independent statuses |
| Adapter fault controls | Wrong errno and polling contamination reject; completed-read/close reply suppression must establish EIO, poison, no replay and no local resurrection |
| Unknown outcomes | Distinguish expected unsuccessful workload cleanup from ordinary success; no generic timeout acceptance or manufactured six-reclaim success |
| Exact package reconstruction | Stage pinned complete artifact set, rebuild the image with pinned tools, reproduce every defined outcome and retain incomplete attempts |

No new receipt format is anticipated solely for libc adaptation. Reuse connections
transport only if its actual envelope, build options and artifact bounds match.
Different client semantics still require an explicit evidence selector and oracle.
Producer acceptance is not package consumption, and package hashes are not signer
authentication or authority to start a service.

## Useful command target: CR-01

Aether's [command-runner proposal](../../docs/NATIVE-COMMAND-RUNNER.md)
selects spawn-only aether-run plus userland bytecount. From the package boundary,
this gives a concrete useful workload to consume after the owners implement and
accept the two-entry standard-file/startup contract. It is not executable on the
complete stack yet, and this note does not approve userland/sys-init policy or
mark the canonical PD review complete.

The proposed payload has runner, command and backend ELFs plus the broker and
kernel boot artifacts. That shape may fit the existing three-image transport;
verify the actual envelope/configuration/bounds when delivered. Do not enlarge
kernel capacity, allocate a new ABI or introduce a package-specific launcher based
on a proposal. Manifest names, argv/env and descriptor numbers remain inert data.

The consuming run should prove the same command image produces exact 6-newline
from abcdef and 0-newline from empty input through real libc EOF/read/write/close.
Retain copied requested argv/env, input preservation, actual child exit, one-time
collection and final cleanup. Keep unknown/denied commands, invalid two-entry
inheritance, whole-request rollback, output-full/short-write, abnormal child and
failed-delivery outcomes distinct. Never substitute hard-coded output or a raw
trap helper for the accepted libc command. Package staging remains inert; sys-init
service admission and ABI-6/ABI-9 composition require separate owner evidence.

## Original UL-052 stopping point (historical)

UL-053's native report/artifacts have not been delivered at this review. CR-01 is
also a proposal pending owner agreement and implementation. The package side is
prepared to consume them; it cannot establish the missing libc/runtime behavior
by changing metadata or replaying UL-051. Other host package work remains possible,
but this integration path needs the next independent consumer. Native shell,
POSIX process semantics, persistent installation and release trust stay open.


## UL-053 consuming checkpoint

The final fourteen-case native consumer has now passed [package staging and boot](evidence/native-inherited-libc-transport-2026-09-05/README.md).
Its source-pinned schema distinguishes it from raw UL-051 clients; inherited
positions remain broker-owned. Deliberately poisoned workloads preserve their
exact unsuccessful outcomes rather than being classified as successful cleanup.
The earlier review-only stopping point above is superseded for this bounded slice.
UL-054's general-size shared reads/EOF remains the next owner handoff; the CR-01
useful-command acceptance above is still future work, not a promoted runtime tier.

## UL-055 consuming checkpoint

[Ten package boot outcomes](evidence/native-fileio-libc-transport-2026-09-05/README.md)
now consume general-size bounded shared read/write and EOF. Each libc call makes
one short transfer of at most 16 bytes with broker-owned position; full 64-byte
storage readback remains independently owner-checked. UL-054's owner-extension
hold is closed. CR-01 still needs its distinct two-record stdin/stdout and copied
startup contract: one inherited record is not a substitute. UL-056's command
workload review is the next userland step; no command-tier acceptance is claimed.

## UL-056 host package checkpoint

The prepared real bytecount command now has a [verified host package lifecycle](BYTECOUNT-PACKAGE.md).
Its unchanged pinned source/license build, register, export/import and run in private
roots. Native command execution remains pending UL-057 and the completed matching
producer handoff. The current runner observes output EOF; exact output byte checks
belong to the designated broker verifier and must be labelled accordingly.

## UL-058/UL-059 handoff review — 2026-09-06

The earlier statement that UL-057 native command execution is pending is superseded
for the finite legacy runner. The current owner bootstrap correction has 22 UBSan
host scenarios, two mutation rejections and nine native legacy regression passes.
The five corrected client ELFs changed and were freshly inspected. The package
review verifies 858 owner evidence files, 293 separately pinned combined-producer
source members, ten native artifacts, all nine recorded images and five changed
client ELFs. [Review identities](evidence/runner-handoff-review-2026-09-06/review.json).
This is evidence inspection, not a package staging/rebuild/boot witness.

The owner receipt is `aether-userland.native-command-userland.v1`; it explicitly
excludes the public aether-run CLI and full CR-01 acceptance. The existing pkg-mgr
native-launch harness has no selector for that receipt. Do not feed it through
userland-fileio-libc or relabel a finite exit-29 runner as the public parser.
Old producer/consumer pins and native transport selectors remain unchanged.

| Boundary | Verified/current owner status | Next package acceptance condition |
| --- | --- | --- |
| Bootstrap publication | CB-01–07: 22 UBSan scenarios, two mutations; failed initialization now terminal/poisoned | Preserve exact corrected adapter/client identities; native injected controls remain separate |
| Transport and malformed replies | CB-08–13 host scope now has 53 UBSan scenarios and two semantic mutation rejections; see the transfer checkpoint below | Native NB-03/04 outcomes remain required; scripted host peer behavior does not prove service completion |
| Native negative boundaries | NB-01/02 now verified (see checkpoints below); NB-03/04 open | Exact owner negative markers and artifact-bound consuming outcomes |
| Public carrier/parser | AERUN001 combined producer reviewed; userland opt-in decoder/parser/consumer is not delivered | A completed, separately pinned userland consumer receipt with case set, artifacts and tools; do not invent its schema |
| Child result/output | Producer mapped-result mode requires admitted/collected child; legacy exact backend output is owner-verified | Separate child kind/detail, parser-selected argv, independently checked output, one-time collection and cleanup |
| Help/local errors/unknown recovery | Zero-admission actions and unknown outcomes lack the mapped-mode acceptance path | Explicit owner contracts and executable witnesses; no relaxed success oracle |

The [owner integration review](../../userland/docs/RUNNER-INTEGRATION.md)
selects local boundary controls, then the pure carrier/parser, then an opt-in
combined native consumer. Aether's producer is available for this work; no new
blanket kernel mechanism request is identified. Sys-init still owns activation
and confirmed-result mapping. Cam owns the pending project reviews, not an inferred
approval of every owner artifact.

When that public consumer is delivered, pkg-mgr should first validate its exact
receipt/case set and input closure, select the matching explicit transport, then
reconstruct and boot its bounded cases from private package staging. None of those
steps permits native installation, deletion, service activation or a new package
core. General shell/make and package storage acceptance remain separate Aether
release prerequisites. ASan remains incomplete; the inspected successful host
instrumentation was UBSan, not ASan or native memory-safety proof.


## Transfer/reply host evidence refresh — 2026-09-06

[Package review](evidence/runner-transfer-review-2026-09-06/README.md) verifies all
810 files in the new owner evidence manifest and its 55 passing outcomes: 53 host
scenarios plus two mutation rejections at exit 90 with distinct no-replay/result
oracles. The adapter matches the prior bootstrap-corrected native input exactly.
The new controls cover short/EAGAIN progress and exhaustion, invalid transfer
results, malformed/dropped replies, consuming close and forbidden frame sizes.
Twenty-four bootstrap and 21 host-command regressions also pass in owner evidence.

This supersedes the earlier CB-08–13 host hold. It does not close NB-01–04, public
UL-059 carrier/parser/consumer adoption or ASan qualification. The initial mutation
compile failure is retained separately; it is not counted as semantic rejection.
No native run was made in this owner slice or package review, and no package runtime,
selector, receipt, standard pin or sibling implementation changed.

The next consumable integration remains a completed, independently pinned public
consumer with its actual artifacts, case set, output/status oracles and build inputs.
Do not fabricate that handoff or rerun the old file-I/O profile as public acceptance.
Aether's combined mechanism is ready; the immediate owner work is native boundary
injection and public consumer implementation in Aether-userland.

## Native bootstrap evidence refresh — 2026-09-06

[Package review](evidence/runner-native-bootstrap-review-2026-09-06/README.md)
verifies 1,117 owner files, 22 ISO/serial pairs and four exact native negative
marker sets. This supersedes the NB-01 hold above. Malformed second reference,
descriptor and rights reject at child 95; early publication is caught at child 97.
Parent 53 and broker 970/reclaimed 0 identify deliberate rejected workloads, not
successful cleanup. Owner channel counters cover adapter calls, not all activity.

NB-02–04 and UL-059 remain open. NB-02 currently has preparation files but no
completed receipt. The 13-case opt-in producer run and nine original-pin regressions
remain finite-runner evidence; no public consumer selector or package boot witness
was added. Native shell/make/storage and actual review remain separate gates.

## Native reply evidence refresh — 2026-09-06

[Package review](evidence/runner-native-replies-review-2026-09-06/README.md)
verifies 1,284 owner files, 26 ISO/serial pairs, four exact negative marker sets
and the unchanged adapter. This supersedes NB-02's preparation-only status above.
The probes consume complete real replies before injecting loss or bad metadata;
failed read preserves the destination, uncertain close remains consumed locally,
and later file/launch/collection attempts issue no adapter calls. The replay
mutant is caught before its forbidden call reaches the service.

Child 84 (mutant 94), parent 53 and broker 970/reclaimed 0 identify deliberate
rejected workloads, not remote recovery. NB-03 launch framing, NB-04 abnormal child
and UL-059 public parser/carrier remain open, as do ASan and actual reviews.
No public consumer selector or package boot witness follows from this inspection.

## Mapped runner handoff verified — 2026-09-06

[Read-only review](evidence/runner-mapped-handoff-review-2026-09-06/README.md)
verifies NB-03/04, startup, result and uncertainty evidence manifests, all 62 latest
combined/legacy ISO-log pairs and client/artifact identities. Ten mapped positives
and six uncertainty rejects have exact terminal-marker checks. Older statements
that NB-03/04 or all parser/startup implementation are pending are superseded.

Next bounded work: a separately named package command-runner transport profile,
exact case-set/identity rejection tests and package-stage consuming boots. The
current receipt still excludes complete public CLI acceptance; local outcomes and
remaining controls stay open. Native shell, filesystem, admission and durability
remain separate R1 gates. No runtime, selector, pin, archive or sibling changes.


## Command handoff preflight — 2026-09-06

`tests/native-command-preflight.py` is a separate read-only development consumer.
It requires explicit evidence SHA-256, build root and client root. It validates
schema, seven enabled modes, the exact 53-case set/polarity, complete native
artifact names, ISO/envelope/log hashes and linked client receipt/ELF bytes/sizes.
It rejects duplicate JSON keys and symlink/traversal inputs and rechecks digests
before emitting its JSON report. Receipt commands are never executed. Recorded
absolute client paths contribute basenames only; the caller selects the root.
This is integrity inspection, not authentication or hostile-race confinement.

Run `python3 tests/native-command-preflight-fixtures.py` for offline schema,
mode, case, path, digest and duplicate-key rejection controls. For the retained
owner artifacts, the exact invocation and successful output are in
[evidence](evidence/command-preflight-2026-09-06/README.md). Use `--help` for arguments.
These opt-in checks are separate from the normal fixture suite. Python remains
development-only. No package runtime/old selector or frozen archive changes.

Next: producer tool/dependency closure, package-stage reconstruction and boot
oracles for the full selected profile. This reader does not perform those steps,
validate every semantic serial outcome, or establish native package installation.

## Package-staged command consumer — 2026-09-06

`tests/native-command-integration.py` adds a dedicated opt-in consumer for the
53-case receipt pinned by tests/native-command-oracles.json. It requires explicit
--evidence, --build, --clients, --aether and a nonexistent --root. The preflight
checks all artifacts before outputs. Only the verified image/smoke tool closure
and boot dependencies are copied from the selected frozen Aether build; setup and
receipt commands are never executed. xorriso/QEMU executable bytes must match the
owner identities. Local Python/make and shell tools remain host prerequisites;
this is not full transitive toolchain qualification.

Each accepted ISO is extracted into an initialized private root. Boot configuration,
license and envelope hashes are checked; existing boot-v2 and connections transports
stage/verify identical bytes before a new ISO is built and booted. The fixed oracle
compares terminal records, supervisor result/reclaim count, panic and success markers.
Uncertain admission alone permits an optional normal child0 terminal, reflecting
scheduling without requiring unobserved completion. All other terminal sequences
are exact. Output bytes remain checked by the independently owned native backend.

`python3 tests/native-command-outcome-fixtures.py` exercises all 53 oracle shapes
and wrong-terminal/cleanup/marker/panic controls without sibling files or QEMU.
Run the integration with `--help` for arguments. It has a 600-second run budget,
120-second owned command groups and the pinned 30-second guest watchdog. Each
attempt retains command logs and incremental case results; only all cases and
final input rechecks permit result.json. No guest network or live disk is selected.
This is bounded transport consumption, not native package-manager execution,
filesystem installation, complete public CLI or unknown-resource recovery.

[Consumer evidence](evidence/native-command-consumer-2026-09-06/README.md) records
attempts, exact inputs and scoped results. These development checks are opt-in;
the normal sixteen-fixture gate remains separately required. Existing profile
selectors, runtime protocols and frozen archive bytes remain unchanged.

Qualification completed: all 53 reconstructed package-stage boots pass, with 22
successes and 31 exact rejections. This supersedes the earlier preflight-only
status for the pinned selected profile. The host fixture suite and explicit
oracle/preflight tests pass; see the consumer evidence above. Next work targets
the actual R1 shell/filesystem/native-admission path, while separately scoped
runner local-outcome extensions remain with their owners.
