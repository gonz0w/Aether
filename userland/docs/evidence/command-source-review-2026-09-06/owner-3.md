# Package consumption: inherited libc and a useful command

2026-09-05. Package-owned acceptance preparation after UL-052. This records our
transport boundary and required consuming evidence, not an implemented native
workload or approval on behalf of another project. Shared requirements and
cross-owner agreement remain in Aether-standards. [Review input pins](evidence/inherited-libc-readiness-2026-09-05/review.json).

## UL-053 acceptance preparation (now consumed)

UL-052 completed the [inherited libc design review](../../Aether-userland/docs/INHERITED-LIBC-PLAN.md).
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

Aether's [command-runner proposal](../../Aether/docs/NATIVE-COMMAND-RUNNER.md)
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
