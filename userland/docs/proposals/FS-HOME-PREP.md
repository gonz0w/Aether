# AF09 engine, helper and image preparation — UL-007/081/082

## Selected scope — 2026-10-24

Live continuation is owned by [GitHub issue3](https://github.com/gonz0w/Aether/issues/3),
with the complete host gate in [issue2](https://github.com/gonz0w/Aether/issues/2)
and native disposition in [issue4](https://github.com/gonz0w/Aether/issues/4).
The separate guarded legacy-profile gap belongs to
[issue56](https://github.com/gonz0w/Aether/issues/56).
This record retains contracts and dated evidence, not a second live queue.

The maintainer requested continued integration until blocked. Following the
[integrated native producer](FS-HOME-NATIVE.md#observed-integration-and-continuation),
this contract describes one offline composition: the real AF09 engine, one explicit
FILE home-write helper, matched guarded owner/shell inputs, pristine/recovery
read-only oracles and exact prepared images. Owner: system integration agent,
preserving userland service/FILE, sys-init lifecycle and root native build roles.

This is preparation, not guest execution. Prior dispositions are consumed. Stop
before any guest; only after concrete reviewed artifacts and a prospective exact
sequence are ready can a fresh disposition be requested. No installation, login,
initial CWD, libc/routed-write activation, package/Zsh/ISO release or durability
claim. Fixed diagnostic names are not an installed home layout.

Apply root PROJECT/METHOD, the owning issue, selected Codex routing, DEVELOPMENT
and affected component guidance/contracts. Preserve native loader/ABI31/AENFS005/
AENMX010 and FILE/context/table/guard contracts, exact consumer pins, old
selections/receipts/seals and smoke/emergency markers. Applicable private standards
and Experience inputs remain owner-provided prerequisites; this contract does not
republish or replace their normative content.

## Input and qualification availability

The public source includes the bounded tools, source contracts and tests. It does
not include private producer/helper/owner qualification receipts, SDK copies,
OpenZFS/runtime build inputs, standards release/review bytes or prepared images.
Obtain the exact applicable inputs from the owner before dependent qualification.
A missing input is blocked coverage, not the expected semantic rejection or a pass.
See the [public-source boundary](../../../docs/PUBLIC-SOURCE.md). Historical
qualification below describes private execution; source-only CI does not replay it.

## Required composition

The distinct explicit preparation paths are:

- `scripts/fs_home_launch.py --checked <producer receipt> --probe-checked <helper/clock receipt>
  --output .deps/fs-launch-af09-*`
  builds and intakes the new engine. Do not weaken AF07/AF08 builders or defaults.
- `scripts/fs_home_inputs.py --engine <directory> --engine-seal <sha256>
  --producer-receipt <receipt> --owner-receipt <receipt> --output .deps/fs-owner-af09-*`
  reconstructs the actual matched owner, shell and helper, measuring their final
  bytes and exact kernel envelope admission.
- `sys-init/scripts/qualify-home-owner.py --inputs <directory> --seal <sha256> --prepare`
  prepares writer, pristine-reader and recovery-reader images and a compact frozen
  receipt. Execution remains outside this selected unit; no guest starts during
  builds, tests, validation or preparation.

Names/flags above select current bounded tools, not public API commitments. Use
existing pinned owned-process helpers and argument arrays, fixed environments,
bounded output, source freezing and exact owned cleanup. Register commands and
native references in workflow before execution. New CLIs use ASCII help/version,
JSON stdout, escaped stderr,0 success/1 failure/2 prerequisite/64 usage, with scope,
receipt/recovery instructions. Never imply renderer or runtime conformance.

The engine links selected native-home.rs, launch-home-owner.rs, integer carriers,
matching policy/service/bridge/activation, home-native.h, checked generated C
engine/importer and original provider/context code. Require one strong definition
and verified object origin for main, all four new home symbols, SPA import/export,
mkdir/Create/write/getattr/context providers. Reject old service/launch symbols,
duplicate providers, unresolved imports, runtime relocations, changed header/
source flags and unexpected origins. New explicit AF09 manifests bind carriers
320/384 and two bootstrap receipts; no cast to old72/136 carriers.

Consume the verified retained SDK/OpenZFS/runtime dependencies. Preserve their
source, license, notices, object/archive identities and input manifests. Never
copy a SDK/repository or retain a per-run source archive. Prefer reconstructing
the original backend object from the pinned recipe and bounded musl internal
headers, comparing its bytes with the unique retained base archive member, then
compile only the existing diagnostic backend overlay. Replace that member in a
copy of the verified UTC archive; every other member must remain byte-identical.
If the existing bounded14-file runtime-source reconstruction is necessary, record
why, verify exact inputs and remove it after use; no whole SDK/repository snapshot.
Fresh composition from retained objects is not an independent rebuild of the SDK.

The existing prepare_engine/compose logic supplies recipe structure. Keep its
old behavior and pins unchanged; use new bounded adapters rather than monkeypatch
modules or bypass checks. Home C generation uses an owned build/ or userland/build/
workspace as required by its existing guard. Reconstruct only needed inputs;
retain source transformation recipes and reject missing/duplicate anchors.

## Current owner component qualification

[Issue64](https://github.com/gonz0w/Aether/issues/64) owns the offline prerequisite
for consuming the current owner admission/deadline evidence. The historical
891-command/nine-control receipt path remains unchanged. A current component
record has a different shape; a larger count alone does not qualify it.

The optional paired `--owner-component-proof` and
`--owner-component-proof-sha256` arguments select one versioned
`aether-af09-owner-component-selection-v1` wrapper and its exact SHA256.
`--owner-receipt` still names the actual component record. Absent selection keeps
the historical interpretation; a partial or malformed selection is usage or
prerequisite failure, never an implicit fallback. Guarded intake persists and
revalidates the same selector through the computed owner-reuse record.

The selected wrapper binds the component record and the reviewed role-file input
impact. The reader validates the complete ordered command/process agreement,
expected exits and control markers, required owner/deadline/transport controls,
frozen implementation inputs, actual tools/libraries and confirmed cleanup.
Only the existing 47 generated C leaves may be reconstructed from their pinned
comparison/header/control recipes. A disposed harness is accepted only when its
retained source bytes match its exact recorded input hash; it is not executed.
No extra unavailable input or actual compiler-source drift is permitted.

The role-file exception concerns the unchanged owner-code-limit value read by
`owner_measure.py`; it is not an owner compiler input. Both role-file identities
and the unchanged measuring source are bound explicitly. An unreviewed role
change, different limit or role-file compiler reference rejects the selection.
The complete owner is still rebuilt and measured from current real sources before
artifact admission. Retained component observations are not a fresh execution,
native peak measurement or proof of parent-terminal/deadline enforcement.

Once fresh producer/helper inputs qualify, the existing offline command can add:

```sh
--owner-receipt COMPONENT.json \
--owner-component-proof OWNER_PROOF.json \
--owner-component-proof-sha256 PROOF_SHA256
```

These optional arguments retain ASCII help/version, stdout JSON, escaped stderr
and the existing 0/1/2/64 success/failure/prerequisite/usage exits. They select no
native workload, guest, new SDK, resource increase or historical 1800-second
builder allowance. Current producer/helper qualification, exact artifacts and
native disposition remain separate prerequisites. Private receipt/proof bytes
remain local under the public-source boundary.

## Current owner fixture selection for host checks

The affected owner reader tests require the exact current component proof and
its SHA256 through a paired host-test environment selection:

```sh
AETHER_AF09_OWNER_COMPONENT_PROOF=/absolute/OWNER_PROOF.json \
AETHER_AF09_OWNER_COMPONENT_PROOF_SHA256=PROOF_SHA256 \
python3 -B -m unittest discover -s tests -p test_fs_home_inputs.py -v
```

Use the same pair for the later complete host gate. These are test inputs;
artifact preparation continues to use the explicit command arguments above.
Missing, partial, malformed, changed or stale selection fails. There is no
newest-file search or implicit historical positive fixture. The selected wrapper
binds the raw component record and its complete source/tool/control closure.
Keep the historical component record for a named stale-source rejection.

A change to a file in that closure requires fresh qualification before selecting
a new proof. Do not exclude a source because it entered through an inventory
rather than an actual compiler command. One complete current owner-component
host run retains all 911 ordered commands, semantic controls, measurements and
cleanup, within its existing 300/180-second and 4 MiB stream limits. A fresh
record may bind equal previous/current role-file identities. Preserve old
receipts and failed attempts; host acceptance remains distinct from native
admission, whole-drain behavior and assembled-system acceptance.

## Fixed workload, authority and completion

Bootstrap remains MakeDirectory(home), Create(probe), empty-file verification,
temporary close and root3/home15 activation, with its existing no-replay and
separate original/normalized receipts. Use one actual source/recipient Owner;
paths and labels1000/1000 confer no authority. No new client, RPC workspace,
descriptor ledger, capability, channel, worker or service.

The C helper uses existing explicit home FILE APIs with AEFD_WRITE_WIRE, required
path/dup2 selections and CWD disabled. It opens existing `probe` through home,
writes exactly the16 bytes `AF09-HOME-WRITE\n` once, checks a fully successful
receipt and attempted offset, closes/reopens, reads exact bytes/EOF and closes.
System-root write access must fail before provider mutation. Preserve source/FILE
cleanup and immutable completion/error receipts on failures; never translate
staged/committed/unknown into success or retry. Success marker `AF09-HOME-WR\n`
fits one16-byte transfer; use helper exit7 with parent0/engine0 as the existing
immutable-helper convention. No old marker changes.

Use a narrow private adapter around the existing context/facade/table operations.
Every direct facade call must hold aefd_native_enter/leave and preserve the actual
authoritative logical descriptor map, slot installation, aliases and final close.
Do not reach into boot.context.client while skipping the guard/table or create a
parallel state model. This explicitly exercises the FILE seam; it does not turn
on libc FILE writes or routed writes for arbitrary applications.

Exactly two bootstrap provider attempts plus one write must be observed. Add
`fs_home_probe_three` with its count check only in the launch success predicate
after the real engine returns: selected success additionally requires
HomeResult.mutation_attempts==3.
Keep foundation default behavior unchanged. Manifest/source/object association
requires this selection. Selected tests hold other valid fields constant:3 passes,
2/4 fail, invalid lifecycle/receipts still fail; unselected2 remains allowed.
No new ABI, marker, count rewriting or kernel observation is needed. Engine0 plus
helper marker and recovery contents alone cannot prove that no extra failed
provider attempt occurred. Shared nine-attempt/96-request enforcement stays fixed.

## Guarded inputs and independent reader

Use a separate exact-member `aether-guarded-af09-inputs-v1` selection and sealed
engine association; do not update docs/native-af07-inputs-v1.json. Preserve kernel
ABI31 and existing AENFS005/AENMX010 envelope bytes. Actual kernel parsers inspect
the final engine/owner/shell/helper, TLS, permissions, lengths and stack admission.
No symlink/path escape, duplicate JSON fields, extra/missing files, old AF07/08
fallback or inferred selection from labels. Measure exact engine/helper pages;
the old1329/33 and1331/34 constants cannot qualify AF09. A freshly measured count
may coincide with an older count; its current artifact, profile and parser result
must still be checked together, with no cached-constant fallback.

Build two fixed read-only native oracles using original OpenZFS read/SA/ZAP APIs,
independent of the writer's Rust bootstrap/FILE path and in a separate fresh SPA.
A bounded `user/storage/openzfs-volume/home-recovery-probe.c` can reuse the existing
inventory/metadata patterns. Baseline requires original full inventory/hash and
home absence. Recovery requires exactly original inventory plus resolved home/
probe objects, correct parent relations, home0700/probe0600, labels1000/1000,
expected ACL/link metadata, fixed16-byte contents/EOF and the unchanged original
780248-byte zstd file. Resolve allocated identities through actual original lookup;
never predict dnode or TXG numbers, check only a prefix, or reuse a pristine-only
reader as recovery acceptance. Check provider errors and bounded allocation/I/O.
The inventory claim is an exact namespace delta, not unchanged parent metadata:
root gains one entry and one link; home ends at size3/links2, probe at size16/
links1 under the existing ZPL rules. Preserve original file bytes/full hash and
unaffected metadata, root identity/parent/mode/labels and other unchanged fields.
Check required root/home/probe mtime/ctime updates against an explicit bounded
writer UTC interval recorded in the prepared receipt, derived from the fixed RTC
selection and existing clock/writer bounds before qualification. Validate legal
nanoseconds and operation ordering where guaranteed by that clock contract.
Do not assume pristine root timestamps, guess inode/TXG/time values, widen a bound
to hide a failure, or reuse the old changed-zstd recovery hash. If the existing
clock contract cannot justify an interval, that oracle coverage stays blocked
rather than skipping timestamp validation.

### Bounded oracle refinements before dependent production

HPET elapsed time is not bounded by delivered PIT interrupts. Enforce the fixed
profile's half-open seconds window `1791290040 <= seconds < 1791290100`, with
legal nanoseconds, through a zero-state delegate to the real RuntimeUtc before
both bootstrap calls, every request mutation and readiness publication. Outside
the window return Clock before effects; default RuntimeUtc stays unchanged. Bind
selection, bounds and fixed RTC input in the engine/prepared manifest. This is an
enforced acceptance window, not an elapsed/physical drift proof or fabricated time.
The independent reader uses the same half-open convention and actual guaranteed
operation-time relationships. Test both boundaries and Clock/no-provider receipts.

Old textual zdb summaries do not provide exact pristine SA nanoseconds/ACL bytes.
The independent oracle returns a32-byte preserved-metadata SHA256 through separate
initialized output: `aether_home_readback(spa, recovered, utc_min, utc_max, digest32)`.
Use canonical ordered, length-delimited scalar/blob fields, never C struct padding
or unstable ZAP order. Compare the full pristine/recovery digest; independently
check the original zstd content SHA256 against its known fixed value. Exclude only
root size/links/mtime/ctime required to change. Normalize root flags by ORing
ZFS_ARCHIVE|ZFS_AV_MODIFIED for hashing and require both bits in recovery; all
other flag bits remain preserved. This is mutation_parent's exact allowed delta.

The new reader checks/buffers its existing32 phase/resource observations internally
(including eight configuration-hash and eight TXG byte observations).
Only after successful read-only close/evict/drain/runtime shutdown and final TLS/status
checks, emit exactly32 eight-byte observation writes carrying the full digest in
their first bytes, with no earlier healthy stdout. Existing numeric kernel rows
then expose32 bytes at offsets0..248 within256 output bytes/32 observations. Old
reader/profile bytes, kernel ABI and quotas stay unchanged; generations2/3 retain
bounded reuse/reclaim checks through their existing B/N/R denial rows, emitted
only after their own runtime/TLS checks, with no digest. Test phase/resource
rejection and late emission.
Controlled transcripts prove parser behavior only. The prospective qualifier must
compare both full metadata digests and retain all media/lifecycle/cleanup checks.

Prepare the prospective fixed pristine-reader -> writer -> fresh recovery sequence
without running it. Bind exact images, source/tool/dependency seals, fixed script,
measured page geometry, payload and reader expectations in the prepared receipt.
Reader media must stay unchanged; writer/recovery use disposable media with exact
canaries and ownership. Prospective trace parsing requires every expected lifecycle,
terminal, wait, cleanup and halt row exactly once; controlled transcripts qualify
only parser logic. Keep distinct bootstrap, service, export/order, actual closes,
stop/reclaim and independent recovery outcomes. Failure stops acceptance; no retry.
The prospective execution must stop on the first unexpected result, confirm owned
VM shutdown and skip remaining guests; preparation authorizes none of those runs.

## Bounds, verification, documentation and simplicity

Preserve owner49152 code/8192 resident including4096 workspace/8184 usable stack/
128 backing pages; engine8192 backing pages; seven domains/twelve channels/35MiB;
writer60s6000 ticks, readers30s3000 ticks and64KiB capture. Loader independently
limits engine ELF8MiB/2048 admitted pages and ordinary process ELF1MiB/128 pages.
Current owner8160 conservative stack leaves24 bytes, not spare permission.
Rebuild and measure actual final composition, not artifact placeholders or local
frames as a peak proof. Failed fit or missing required input is blocked coverage.

Before implementation write meaningful expected/forbidden tests and retain red
when executable; missing APIs are compiler red, not semantic execution. Include
helper guard/map/close/receipt failures, selected/unselected launch counts, strict
receipt/seal/flags/carrier/origin/member denials, wrong-profile/TLS/WX/envelope and
actual loader checks. Reader host tests execute the actual oracle with typed
substitutes and reject inventory/metadata/payload/EOF corruption; compile original
target headers/providers. Compiling omission controls need named semantic failures.

Use focused suites during iteration. Register `check-home-probe.py` and
`scripts/check_fs_home_prep.py` before execution for the helper/launch and root
preparation/oracle checks respectively; each host suite has300 seconds. Individual
build children stay180 seconds and offline target composition1800 seconds. New C
uses Clang21.1.8 C17/UBSan/format; Rust1.98/2021 userland fixtures and2024 sys-init
keep their scoped flags and strict Clippy. Python uses current pinned development
interpreter and owned-process behavior. No network/setup/install is part of runs.

Before the actual integration handoff run zig build test once on final source,
complete affected native/component builds, final selected producer/helper/reader
and actual-owner measurement. Reuse unchanged component results only after explicit
source/impact checks; changed required inputs need fresh qualification, never a
rewritten old receipt. Freeze sources during qualified builds; perform omission
tests first. Full SDK cold-build, native peak, physical, extended and release
evidence remain outside this bounded preparation.

Record live acceptance and continuation in issue3; keep component references and
root workflow consistent with this contract. Separate source/control/evidence/
reader review precedes integration under public PROJECT policy. Preserve all failures, commands, hashes and short logs;
remove owned generated work. Keep only the single current verified dependency and
exact pending artifact set needed for the next disposition, not historical image/
binary/SDK/source bundles. After a run finishes remove owned outputs per retention.

Simpler alternative: swap AF09 objects into the old AF08 path and reuse its reader.
It trusts wrong symbols/carriers/pages, lacks the helper guard/map write selection
and never checks home recovery. Reuse original build/loader/provider/context/table
logic with explicit new associations and a fixed workload, preserving old inputs.
No generic filesystem, provisioning, rollback, parser platform or new authority.
No obsolete sealed path is removed yet; limit added mechanisms to this executable
experiment. Unix responsibilities remain separate while one integration agent
composes them.

## Offline commands

With exact private prerequisites available, run from the system root and choose
unused output directories:

```sh
PYTHONOPTIMIZE=1 python3 -B userland/experiments/filesystem-service/check-home-probe.py
PYTHONOPTIMIZE=1 python3 -B scripts/check_fs_home_prep.py
python3 -B scripts/fs_home_launch.py --checked PRODUCER_RECEIPT --probe-checked HELPER_CLOCK_RECEIPT --output .deps/fs-launch-af09-NAME
python3 -B scripts/fs_home_inputs.py --engine .deps/fs-launch-af09-NAME --engine-seal ENGINE_SEAL --producer-receipt PRODUCER_RECEIPT --owner-receipt OWNER_RECEIPT --output .deps/fs-owner-af09-NAME
python3 -B sys-init/scripts/qualify-home-owner.py --inputs .deps/fs-owner-af09-NAME --seal INPUTS_SEAL --prepare
```

The two checkers retain their own host-check contracts. The three preparation
CLIs provide `--help`/`--version` on stdout and JSON success results on stdout,
with escaped operational diagnostics on stderr. Their exits are0 success,
1 operational failure,2 blocked prerequisite and64 usage. Preparation has no
execution option. Retain the compact failed receipt, correct the prerequisite
and select a fresh unused output; never edit an old result into success.

## Unconfirmed host-process cleanup

If an owned child cannot confirm shutdown, fail preparation and retain its work
and related outputs. The failed compact receipt reports unresolved cleanup and
retained paths; a nested intake propagates that state to the outer builder.
An interruption before the process helper returns also leaves shutdown
unconfirmed. Do not remove or reuse those paths until shutdown is confirmed.
A failed command with confirmed shutdown keeps the ordinary owned cleanup path.
Receipt publication failure must preserve the original failure and retained work.

The public host wrappers enforce this failure behavior with mocked direct,
imported and nested-child controls. These controls create no orphan or guest.
The corresponding target source, compilation arguments and native limits are
unchanged; the dated private qualification below remains tied to its original
source maps. The public port has separate affected host checks and source review,
not a new complete private gate or public native qualification.

## Private offline qualification summary —2026-10-25

Private preparation produced three exact images after2072 bounded children,
including six expected normal exit1 linker denials. Source/tool/receipt and
publication checks passed, with owned intermediate cleanup. The complete owner
measured47384/49152 code,7784/8192 resident including4096 workspace, and8160/8184
conservative stack. Writer loader geometry is engine1334/shell81/helper34 pages;
each independent reader admits1318 engine pages. The reader controller is1012
bytes. Conservative fit is not native peak evidence; its24-byte stack margin
confers no additional capacity.

[Issue2](https://github.com/gonz0w/Aether/issues/2) records the separately reviewed
complete unfiltered host attempt05:530.184 seconds within its one-run900-second
aggregate,976 Python tests with terminal OK, final sources/tools and accepted
legacy-pair checks,9115 prepared inputs, six image/kernel identities and owned
cleanup. Attempts01–04 remain failed and preserved privately. The900-second
exception is consumed; default host300, leaf/auxiliary180 and live4MiB diagnostic
streams remain. No automatic retry or guest permission follows.

These are dated private results, not public-clone replay or native acceptance.
Private compact receipts, artifact identities and earlier failures remain with
the owner; none of their raw contents or generated artifacts are published here.
Public source integration is recorded in issue3. Issue56 is separate guarded
legacy coverage. General recovery and power-loss durability, full SDK cold rebuild,
native peak, physical/extended coverage, interactive Zsh and release qualification
remain open. The separate bounded native witness below does not close those gates.

## Bounded native witness —2026-10-25

[Issue4](https://github.com/gonz0w/Aether/issues/4) records one authorized
pristine-reader -> writer -> fresh-recovery QEMU sequence. All three roles passed.
The writer completed the fixed bootstrap and C FILE workload with the required
helper, parent and engine terminal outcomes. Independent recovery checked the
home/probe payload, original file and complete preserved-metadata digest.
Both reader runs left the whole media unchanged; recovery consumed the exact
confirmed stopped-writer media. Strict wait, terminal, reclaim and host shutdown
checks passed. Source, tool and artifact verification remained valid.

A separately reviewed temporary execution driver supplied the AF09 serial input
and used the existing strict transcript/media oracles. Offline controls tested
sequence failure, stale inputs, capture bounds, partial writes, deadline accounting
and unknown shutdown. All guest process groups were confirmed absent before owned
outputs were removed. Current dependencies and compact evidence remain private;
the consumed prepared images and temporary execution files were disposed.
Retained hashes do not make those artifact bytes available for replay.

This is bounded native bootstrap, FILE-write and fresh-recovery evidence.
It does not qualify general operational uptime, installed-home/login policy,
power-loss durability, interactive Zsh or R1. The public preparation qualifier
still has no execution option. Another native run needs fresh reviewed artifacts
and its own disposition. The next service-lifetime contract is tracked by
[issue9](https://github.com/gonz0w/Aether/issues/9); that issue owns selection and
acceptance rather than this dated witness.
