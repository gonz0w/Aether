# UL-067 native cat owner review packet

Prepared 2026-09-06 for Aether's UP-02 command owner. At the user's explicit
request, recorded in [Aether UP-02 planning](../../aether/.planning/ROADMAP.md#ul-067-intake-bounded-native-cat-producer-2026-09-06)
and its STATE intake note. This is planning receipt, not design acceptance.
The native follow-on is waiting for
reviewed producer inputs. [CAT-01–08](TOYBOX-NATIVE-CAT.md#proposed-native-acceptance-matrix)
remain the local acceptance plan, all native NOT RUN. This packet does not create
a shared standard, native ABI or package policy.

## What userland has established

| Evidence | Demonstrated scope | Remaining boundary |
| --- | --- | --- |
| [Standalone comparison](evidence/toybox-standalone-2026-09-06/summary.json) | Unmodified Toybox cat/wc build and Linux behavior; cat79,888 bytes; default ELF reproduced | Static size is not native memory fit or security |
| [SDK audit](research/TOYBOX-NATIVE-SDK.md) | Exact native SDK inventory, built-in locale selection, unsupported umask and stdio writev paths | No native cat build or call-graph completeness |
| [Host components](../experiments/toybox-reference/README.md) | Finalizer, vector, session and mask state with UBSan, semantic mutants and bounded negative controls | Logical roles/callbacks are not grants or native reclaim |
| [Actual stdio loop](evidence/toybox-stdio-loop-2026-09-06/summary.json) | 9,720 Linux callback cases, pipe control and two mutants | Internal FILE write loop, not full public stdio/native lifecycle |
| [Combined Toybox](evidence/toybox-composed-2026-09-06/summary.json) | Actual startup, mask save/restore, scalar/buffered writes, flush and finalization; eight cases plus compiled mutant | Link-time Linux fixture, no native patch, startup-role carrier or acceptance |

All prior attempts, exact source/patch/SDK/tool/artifact identity and logs are retained.
The combined fixture's observer is a duplicate Linux stderr handle, not a proposed
native capability. It lets tests observe after logical stream closure; the native
producer needs its own authoritative verifier. Linux process exit is not an Aether
reclaim witness. Source trust, independent review and packaging remain open.

## Current producer review

The command-I/O contract, native-command owner, native-connections supervisor and
native-files backend still match the earlier reviewed bytes. They admit bytecount
with child stdin0/read and stdout1/write, with a fixed two-entry bootstrap and
64-byte output fixture. They do not define a child diagnostic role or cat identity.
The [review receipt](evidence/toybox-owner-handoff-2026-09-06/summary.json) records
current hashes independently of the owner's evolving STATE.

Aether's STATE now records opt-in larger images/memory and bounded native threads.
Those are separate owner profiles, not an adopted SDK or child-I/O extension.
The pinned single-thread consumer contract remains unchanged; no thread support
is inferred for mask/session callbacks. Reassess exact dependencies if a new
producer bundle selects those profiles.

## Requested Aether decisions

| Decision | Concrete requested result |
| --- | --- |
| Cat admission identity | Select a separate opt-in image/profile and exact accepted command/startup; preserve bytecount, mapped and legacy profiles. No authority comes from argv[0] |
| Child diagnostic role | Define complete bootstrap/version/bounds, rights, generation and lifetime for distinct input/output/diagnostic bindings; reject partial/misordered/aliased/wrong-rights publication |
| Bounded test storage | Review finite input up to32 bytes, exact output/prefix and separate diagnostic capacity sufficient for explicitly pinned error text; keep opposite outputs/input unchanged on rejected startup |
| Startup state | Decide ownership/source of initial process mask (proposed0077), exact environment and native memory/TLS grants. Do not add a successful no-op umask or promote generation labels into authority |
| Failure and cleanup | Independently observe consuming closes, poisoned/no-replay transport, actual diagnostic failure and abandoned local bindings; specify terminal/forced-stop cleanup and real per-generation resource totals |
| Trusted verifier | Bind expected argv/action/content to owner fixtures, verify actual bytes and no-read rejection, then prove normal/error/abnormal-stop reclaim over two generations with skipped/wrong-prefix/omitted-close controls |

Child stderr is not the same as UL-059 runner-local stdout/stderr. Review their
possible common transport once, but keep acceptance workloads and resource
inventories separate. Do not reuse no-child runner reclaim totals for a cat child.
No exact new wire field, syscall, broker budget or reclaim total is assigned here.

Suggested owner planning text under existing UP-02: review an opt-in cat child
profile for userland UL-067/CAT-01–08, including child diagnostic authority,
independent byte/lifecycle verifier and exact startup/mask decisions; supply an
immutable producer contract/source/evidence bundle while preserving current modes.
The owner chooses its implementation sequencing. This request is now recorded under Aether UP-02; the existing R1-03 priority is
preserved.

## Userland patch boundary after review

Userland owns the eventual bounded argument gate, process-mask state, private
stdio bridge and candidate-local termination seam. Before calling Toybox, validate
its entire startup and required roles. Preserve normal Toybox initialization;
review a scoped stdio callback change rather than a global syscall interception.
The recommended terminal seam is after xexit callbacks/flush and _xexit rebound
handling, before _exit. The Linux wrappers are test instrumentation, not the patch
to ship. Native entry, direct/indirect/abnormal exit reachability and shared poison
state must be re-reviewed against the actual selected source and owner contract.

No filename/option/help/version support follows from the first stdin-only profile.
The reference -e tests cover buffering and do not widen proposed native admission.
Pin exact adapter rejection text before implementing that gate. Known command
errors stay nonzero; unknown writes cannot trigger fresh diagnostics/closes or be
reported as no effect. Real owner-side reclaim remains separate from local state.

## Return bundle and acceptance sequence

Return exact reviewed profile/contract identity, compatible startup/role version,
initial-state ownership, tool/SDK/flags/environment identities and full resource
inventory. Include regular-file source archive/manifest, artifact hashes, raw
serial/verifier output, all failures/incomplete attempts, cleanup facts and explicit
CAT case status. Identify affected-owner decisions and unresolved cases; do not
change userland pins on its behalf.

Userland verifies the bundle, reviews compatibility and explicitly selects the new
pin before consuming it. Then build independent native clients/adaptation, inspect
ELF and unsupported syscall paths, run CAT-01–08 plus relevant existing regressions,
and retain semantic rejection controls. Independent review and source/payload trust
still precede supported packaging. pkg-mgr recipes and sys-init policy stay with
their owners; this packet requests neither implementation here.

Native UL-067 now waits at this producer boundary. UL-059 retains its own pending
[runner-local handoff](RUNNER-OWNER-HANDOFF.md). Only the explicitly requested ROADMAP/STATE intake was added to Aether. No
message, monitor, runtime change or owner sign-off was created; no whole-system
or POSIX shell readiness is claimed.
