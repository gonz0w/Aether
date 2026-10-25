# Native executable replacement with a live pipe

## Requirement and review before implementation

Use the existing parked-image replacement primitive to run a real external writer
inside actual dash command substitution. The private connection owner validates
the complete five-binding descriptor table before admission; a denied image must
leave it and pipe ownership unchanged. Successful admission drops CLOEXEC aliases,
preserves the stdout writer and parent reader, then publishes replacement startup.
Only the boot-granted third image may execute. Paths select a scoped request;
they never confer image authority. No kernel API, quota, SDK or sibling changes.

The bounded workload is `value=$(/next); result=$?; echo "$value"; exit "$result"`.
Before real exec the child probes denied admission and checks retained aliases.
FD10 (stdin) and FD11 (writer) have CLOEXEC; stdout retains the same pipe writer.
The replacement validates startup, surviving descriptors, pipe generation, mask
and process generation before writing exactly `pipe\n`. Parent drains through EOF,
collects the actual zero child status and acknowledges it before reclamation.
Run two complete parent/backend/child lifetimes within existing six-reclaim limits.

Forbidden: early EOF, alias/peer closure, authority growth, stale commit, successful
return from exec, unvalidated startup I/O or invented status. Denial cancels the
exact freeze and returns EACCES without a holder transition. Admission commits the
image while frozen, checks its retained image receipt, commits holder/descriptor
policy, resumes and delivers bounded startup. Unknown outcomes fail closed; general
interrupted publication/reconciliation is not added or claimed here.

Simplicity SE-01–SE-05: reuse existing exec staging, the descriptor filter, pipe
core and dash fork/wait. A builtin writer cannot establish executable replacement;
a generic process-service framework is unnecessary. This scoped connection-owner
branch keeps policy outside the kernel and adds no service. Existing consumer
profiles stay until replacement is qualified. No obsolete path can be removed yet.

Apply Foundations O-02–O-04, I-01/I-03–I-06, E-01–E-06 and the local development
process. Existing released pins remain fixed. Rust uses toolchain 1.98.0 edition 2024;
touched C uses the existing pinned Clang 21.1.8 formatter configuration. No new unsafe
Rust/assembly boundary: copied byte arrays and existing bounded IPC helpers carry
startup; C stack records stay live through synchronous transfers. New replacement
code retains upstream musl runtime and its existing flags/license.

Select focused native positive and semantic controls (stale pipe commit and dropped
surviving writer), host/harness checks, pinned simplicity verification, C/Rust format
and the complete connections regressions. Freeze sources and retain every attempt.
Update the existing native reference and workflow profile inventory, STATE and
companion coverage. Native SDK/independent consumer acceptance, serial composition,
interruption and R1 assembly remain separate.

## Results

All 277 connections QEMU cases pass in 841.66 seconds on frozen sources, including
three new pipe-exec cases. The full host suite passes (100 Python tests plus Zig
checks, including 23 pipe/descriptor core tests); C/Rust formatting, workflow,
immutable standards pins and the separately pinned simplicity manifest/four files
pass. The new owner is 13,840 bytes within the unchanged 16,384-byte bound. All 89
previous copied-fork C ELFs remain byte-identical.

The positive runs actual dash with an external `/next` substitution in each of two
parent/backend lifetimes. Each copied child first receives actual EACCES from the
native image gate and verifies retained FD10/11 flags, then is replaced by the
third boot-granted ELF under freeze2. The replacement validates its fresh TLS,
arguments, full startup records, zero saved mask and missing CLOEXEC aliases before
writing through the retained stdout pipe. Parent drains exactly five bytes and
EOF, echoes the captured value to an independently read-back backend, waits for
the real zero status and acknowledges it. Child0/parent0/backend17 in generations1/2
produce six real reclaims. No extra process or quota supplies that count.

Stale pipe generation rejects2184 before replacement startup, with zero reclaims.
Dropping the surviving stdout table entry causes replacement227/owner2176, with
zero reclaims and no successful pipe output. The private diagnostic identifiers
retain the exact rejection stages. Matching trace extraction is recorded in
`native-traces.json`; commands, images, flags, tool/dependency digests and source
hashes are in `connections-results.json` and the verified archives.

No kernel source, new ABI, SDK, sibling repository, upstream dash object, released
pin or resource quota changed. The new original C replacement is BSD-2-Clause and
links the existing pinned musl runtime. The generic PIPE+EXEC build combination
remains rejected; this dedicated test branch is not an installed SDK adapter.

Next adopt this qualified external-substitution path in interactive serial dash,
including repeated pipe/child generations and clean shell replacement. General
interrupted publication/copy rollback, concurrent pipelines, SDK delivery,
independent userland acceptance and R1 filesystem/package/sys-init assembly remain
open. The separate launch and console-only suites were not repeated; their runtime
paths do not consume this opt-in branch, and existing serial-dash cases are included
in the complete connections suite. No full shell or release-readiness claim follows.


## Retained preflight attempts

| Attempt | Outcome and correction |
| --- | --- |
| 1 | Driver import failed before native harness setup. Added the original scripts directory to its module lookup. Original driver is retained. |
| 2 | Rust compilation rejected a 32-byte word helper used on a 128-byte startup record. Used bounded slice copies at the correct offsets. |
| 3 | Loader rejected the replacement ELF because the fixture requires a TLS segment. Added an initialized private TLS cookie and checked it on replacement entry. |
| 4–6 | Native admission rejected at 2183 with zero reclaims. Split validation failure identifiers to distinguish framing, table, mask, freeze and image checks; no successful run was claimed. |
| 7 | The refined check rejected at 2301: the receiver requested all 272 argument bytes in one call, exceeding the 256-byte channel limit. Read 256+16 bytes using the existing bounded helper, matching the old exec receiver. |
| 8 | All three focused QEMU cases pass: real external substitution and both named controls. This selects the three new profiles from the current harness AST; the complete unmodified harness is used for final regression qualification. |

Failed source snapshots, raw build/serial output, exact commands and timing are
retained alongside the verified attempt archives. Additional validation identifiers
2185–2191 and2301–2305 distinguish the descriptor/mask/freeze/argument/image and
transport/publication stages; they add no new native wire operation. No source
changes occur during final qualification. Archive compression uses gzip level 1;
all member hashes are verified against their source files after writing.
