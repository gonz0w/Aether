# Bounded root file paths — UL-007/081/082

2026-10-23. Pre-code requirement and review for the next persistent shell/loader
slice. This is a separate fs_paths client selection, not a new POSIX open/CWD API,
selected shell profile, native acceptance or shared standard. Root STATE governs
system integration. Existing component lookup and default client stay exact.

## Requirement and interface

Add Client::open_root_path(path) using the client's actual delegated AF07 root.
Accept one canonical root-relative or single-leading-slash path,1–255 bytes total,
with nonempty components. Reject NUL, dot/dotdot, repeated/trailing separators and
oversize paths before any source effect. Root '/' denotes a directory and returns
EISDIR(-21) locally. These are canonical image/file paths, not POSIX normalization,
CWD-relative interpretation or symlink resolution. Do not manufacture getcwd('/').
Names/paths never authorize endpoints or objects. Initial trusted root delegation
must include LOOKUP|READ3; intermediate directories request3 and final file READ2.
No new rights, payload, RPC, worker, memory, channel or runtime lifetime allowance.

Use existing authenticated component lookup/close only. Keep root and all preexisting
handles; allocate at most two transient handles (previous directory plus next
entry), independent of depth. Preflight one free slot for a single component or
two for a walk, and enough monotonic token space for every component. No counter
reset/reuse, heap, cache, recursive traversal, handle stack or writable static.
The existing16 bindings,255-byte name/64-byte frame/4096-byte data limits remain.
No new Client fields/layout or change to AF07 wire, old lookup, broker or libc.

Every intermediate result must be a directory; final result a regular file.
Wrong intermediate type closes temporary handles and returns ENOTDIR(-20); final
directory closes its temporary handle and returns EISDIR. Only the returned file
handle remains live, for existing read/stat/close. No executable authority follows.
Existing service decoding determines supported node kinds; do not follow a link
or infer an object identity from a name. Filesystem mutation/immutable executable
admission and per-process CWD remain separate contracts.

After each next lookup, close only the previous temporary directory. On known
lookup error, close that directory then preserve the original errno if close
succeeds. Any failed close overrides the lookup/type result and retires the
client through its existing fatal-close behavior. If lookup already retired the
client, send no subsequent close/replay. A parent close failure also invalidates
the newly returned handle; do not publish it. All endpoint-close results and
once-only drop/unknown ownership semantics remain those of the original client.
Exclusive synchronous borrow serializes the walk; no coherent namespace snapshot
across concurrent rename is claimed. Each actual lookup remains service-enforced.

## Security, simplicity and review

Apply pinned O-01–05/I-01–06/E-01–08 and approved CE/CD/CA/TD/SE-01–05. The untrusted
input is the path; protected state is the scoped client binding/token ledger and
existing open descriptions. Check the full syntax, source rights and capacity
before requests, and type/identity/error/cleanup on every reply. No unsafe code,
FFI, assembly, dependency or authority transition is added. Existing original
BSD-2-Clause sources/tools and exact sealed service/tool pins are reused.

Simpler alternative: split paths in the caller and expose raw handle management.
Insufficient: it duplicates the current loader's needed cleanup/type/retirement
obligations, or leaks directory handles across a long path. Reuse proven AF07
component capability traversal with one rolling temporary; no generic VFS/mount/
symlink/CWD framework. No compatibility path is removed. The opt-in feature keeps
all current component-only consumers/profiles exact; a later broker/loader consumes
this tested operation only after explicit binding and full resource measurement.

Implementation-agent technical review only; independent reader/owner/native and
release acceptance remain pending. Do not mark UL-007/081/082 or R1 complete.

## Planned checks and documentation impact

Test actual client bodies with scripted malformed/short/error/close outcomes and
the real sealed Rust AF07 service/policy over bounded host channels with synthetic
storage. Verify relative/absolute/single/deep/max paths, actual file bytes, every
component/rights/token/close order, root retained, unrelated handles live, invalid
full paths with no effects, capacity/token exhaustion before effects, wrong type,
known error preservation, failed intermediate/final close, fatal lookup/no replay.
Compile semantic controls for skipped directory close, skipped preflight, parent
rights attenuation that makes the final READ invalid, missing type checks and
root-escape syntax acceptance. Every control must compile and fail its semantic
oracle, not merely break imports. Keep all previous13 client tests under the opt-in
selection; compile/test the default selection separately on the same sources.

Use pinned Rust1.98 and strict format/Clippy/unsafe-denial, host and
x86_64-unknown-none no_std libraries. No native script or quota change in this slice;
measure unchanged Client layout and retain code/library hashes without claiming
whole-owner fit. New checker works offline under userland/build, bounds every
subprocess, freezes live inputs, preserves short failures/commands/hashes and
removes generated sources/binaries after compact readback. No full build archive.
Run userland docs/quality/check.py and root workflow check; update coverage/STATE/
README and command reference. Exact checker command is added before execution.

## Scoped broker consumption, before implementation

Consume the operation in Remote::open_read only when fs_paths is explicitly
selected. The existing shared-description/process-view APIs remain available;
this selection interprets their read name as a canonical delegated-root path.
The default keeps component semantics. This phase does not select a new FILE wire,
change C/libc open, add CWD or enable it in the native owner. It makes the tested
path walk usable by the existing Rust descriptor/loader consumer rather than
leaving callers to manage raw handles. No new fields or capacities.

Retain all8 default remote-descriptor regressions. Under fs_paths retain the7
applicable existing cases and add nested read/alias/offset/close and full-table
capacity-before-lookup/error cleanup cases; the old component-only invalid-name
case remains default-only, with new path cases supplying its selected counterpart.
Build strict host/native libraries for this actual consumer, compare baseline/
selected Client and Descriptors size/alignment, and keep full native-owner fit/
protocol/CWD/loader integration pending. Do not claim native inheritance or grant
validation from host synthetic storage.

Command, from userland/: `python3 -B experiments/filesystem-service/check-paths.py`.

## Results and next authority boundary

Implemented fs_paths in Client and the actual Remote descriptor consumer. Focused
checks pass22/13 selected/default client tests,9/8 selected/default descriptor
tests and five compiling controls; strict format/Clippy/unsafe checks and native
no_std libraries pass. Both layouts are unchanged. Initial two harness failures
and the final commands/hashes are retained in [evidence](../evidence/filesystem-root-paths-2026-10-23/README.md).
Default AF07 inputs were refreshed without selecting fs_paths; actual native owner
remains39376 code/7504 resident/8000 conservative stack. No guest or path-enabled
whole-owner fit is claimed. Minimum Python3.10 execution remains missing; current
3.14.7 passes. Independent review/native/R1 remain open.

Maintainer decision2026-10-23: writable home for the interactive shell; system
changes only through an explicit installer/admin operation. Do not widen the
current read-only client to a mutable system root. Trusted provisioning must bind
home mutation authority to a real delegated directory/service connection, separately
from system reads and admin installation authority. Absolute path text, HOME/UID,
package state and mode bits cannot mint that grant. Bind allowed objects/rights
before readiness and preserve inheritance/exec/retirement checks. Home location,
CWD and the concrete bounded multi-root binding belong in the next local contract;
no new service/channel/worker/memory quota is authorized by this policy choice.

## Explicit path FILE wire, pre-code scope

Next implementation: select fs_path_wire only together with fs_paths and
fs_process_views. AEFP0001 is a distinct private8-byte request/reply magic;
AEFD0001 stays component-only with identical defaults. The trusted owner and
client build must choose the same variant; never infer it from peer bytes or fall
back on mismatch. No live auto-negotiation, mixed client multiplexing or grant
change. Wrong variant must fail the existing protocol/retirement boundary before
filesystem effects. The existing16 FD slots/four process views,64-byte frames,
256-byte padded name input,4096-byte workspace and once-only reply settlement
remain unchanged; no new fields or allocation.

AEFP opcode1 consumes the canonical delegated-root path operation above. Other
opcodes/shapes/sequence/error/cleanup remain exact. C codec uses explicit
AEFD_PATH_WIRE build selection, validates the entire1–255-byte canonical path
and clears all256 output bytes on rejection. Root '/' is syntactically valid;
Rust reports EISDIR. Body tail must still be zero. No public POSIX relative path,
CWD, symlink, writes, executable loading or libc slash support is supplied here.
Existing libc slash rejection remains truthful until its own binding contract.

Tests: actual selected ProcessFiles/Connection and sealed AF07 service with C
requests/Rust responses/C validation; nested paths, inherited FD/shared offsets,
root and traversal errors, known errors preserving root, capacity and once-only
intermediate cleanup, malformed padding, dropped/forgotten reply and explicit
old/new variant rejection before effects. Retain9 existing default protocol tests
and eight compiling semantic controls; selected path variants retain applicable
cases and add path/variant cases. Strict C17/UBSan, Rustfmt/Clippy/unsafe denial,
freestanding library builds and exact input hashes; independent/native owner fit
and native execution remain separate. Existing checker command with --paths is
the selected recipe; without arguments preserves default checks. Root workflow,
component quality/README and compact evidence are updated. Security/simplicity:
one explicit versioned selection composes the existing operation; no generic
path service, new rights or ambient namespace. No shared/released pin changes.

Path-wire results:11 selected/10 default Rust tests, eight compiling controls
per selection, actual C/Rust/C interoperability and C17/UBSan codec bounds pass.
Opposite wire and mismatched broker dependencies reject. No new fields or native
selection. [Compact results](../evidence/filesystem-path-wire-2026-10-23/README.md).

## Complete owner consumption and read probe

[Sys-init0221](../../../sys-init/docs/decisions/0221-root-path-owner.md) supplies
explicit matching producer/provider/owner selections and a dispatcher using its
bound handler's magic. Optional libc permits the canonical root paths under
AEFD_PATH_WIRE; default slash rejection remains. This private bridge still has
root-relative semantics, not real POSIX CWD. The complete selected owner fits
40640/49152 code,7504/8192 resident and8000/8184 conservative stack with no quota
increase. Native initialized-TLS shell/helper fit80/33 pages. No disk image bytes
are executed; the optional immutable helper probes read/count/size/EOF/close only.
Independent full-file/media verification remains mandatory. Host/build coverage
and two initial mock-only failures are in
[results](../evidence/filesystem-path-owner-2026-10-23/README.md). Native path and
independent/R1 acceptance remain pending, with current limits and stop-first-failure.

## Directory-anchored walk foundation —2026-10-23

Pre-code UL-007/081/082 continuation: a real CWD must resolve from a retained
service directory, not a synthetic path string or a fresh system-root lookup.
Under existing fs_paths add Client::open_file_from(directory, relative_path) and
open_directory_from(directory, relative_path). They accept nonempty canonical
relative paths up to255 bytes. Leading slash, NUL, empty/dot/dotdot components,
repeated/trailing separators and oversize paths reject before requests. Root and
unchanged open_root_path preserve existing semantics (including '/' EISDIR).
Callers use root() for the borrowed root handle; these new walks always return
one newly owned handle. They never alias ownership of the input directory.

Validate the exact live connection-scoped base binding, Directory type and
LOOKUP|READ3 before effects. A live non-directory base yields ENOTDIR; stale or
insufficient-rights bases reject locally. No fallback to root or implicit rights.
Directory results carry3; file results2. Preserve the input base and all unrelated
handles, preflight one/two transient slots and all monotonic tokens, and close
only owned walk temporaries. Final wrong kind closes the result then yields
ENOTDIR for requested directory or EISDIR for requested file. Known lookup errors
survive successful cleanup; uncertain lookup/any failed close retires the client
once, with no subsequent request/replay. Exclusive synchronous borrow prevents
local reentry; concurrent server namespace changes remain ordinary per-lookup
semantics, not a coherent snapshot or a POSIX getcwd guarantee.

Security/simplicity: reuse the rolling existing walker and private typed terminal
check. Copying strings in the shell cannot preserve service directory identity;
a second resolver, handle cache or VFS is unnecessary. No compatibility path is
removed. New methods add no Client/Descriptions fields, capacity, allocation,
unsafe/FFI, dependency, authority, wire or native selection. Pinned O-01–05,
I-01–06/E-01–08 and approved CE/CD/CA/TD/SE-01–05 apply. No mutation grant follows
from a directory name, HOME or UID. Writable-home provisioning, process CWD
retention/inheritance/getcwd/chdir semantics and matched public protocol remain
separate next integration work; these methods alone claim none of those.

Focused command remains `python3 -B experiments/filesystem-service/check-paths.py`
from userland. Retain all old selected/default client/descriptor tests, add real
sealed-service directory→file/close cases and exact base token/rights traces,
foreign/stale/file/rights/capacity/counter/escape denials, wrong terminal kinds,
known/fatal lookup and failed temporary-close cases. Compiling controls must catch
root substitution, base type omission, directory rights attenuation and result
kind omission, alongside existing preflight/cleanup/path controls. Strict pinned
Rustfmt/Clippy/unsafe denial and host/target libraries/layout comparisons apply.
Update existing workflow/coverage/review/README; compact hashes/results/failures
only. No guest or repeated broad suite: native active dependency bytes remain
frozen, and changed future selected owner needs fresh complete fit/disposition.
Review is by implementation agent; minimum interpreter/independent/native/R1 gates
remain open.

Directory foundation result:30 selected/13 default client tests,9/8 descriptor
tests and eight compiling semantic controls pass. Real sealed AF07 service and
scripted exact-base/rights/cleanup checks, strict Rustfmt/Clippy/unsafe denial,
host/target libraries and unchanged680/1128-byte Client/Descriptions layouts pass.
Actual selected FILE consumer15 cases/ten controls/C-Rust-C/C17/UBSan/target checks
pass. Two harness failures remain in [compact evidence](../evidence/filesystem-directory-paths-2026-10-23/README.md).
No new native input selection or VM; complete owner with future retained process
CWD still needs measurement/qualification. Current Python only, minimum3.10 and
independent review missing. Current bounds/releases/sealed deliveries unchanged.
