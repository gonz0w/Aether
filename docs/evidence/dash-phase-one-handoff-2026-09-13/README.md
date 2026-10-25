# Dash phase-one producer handoff — 2026-09-13

Requirement: provide one review entry point for UL-007 startup, arguments,
signal-table and syntax without changing runtime behavior or installing an SDK.
Aether owns the private native adapters and enforcement; userland owns independent
consumer acceptance and the supported libc integration boundary (UL-081).

Forbidden: treating historical startup/syntax evidence as a fresh combined run,
overwriting sealed evidence, installing fixture adapters, changing sibling files
or released pins, or claiming the twelve-workload gate or R1 is complete.

This is documentation and evidence assembly. Applicable Foundations E-01–E-08
require pinned inputs, private replay outputs and scoped claims; Distribution
PX-01–PX-03 keep adapted semantics and consumer ownership explicit. No authority,
ABI, quota, unsafe boundary, dependency version or runtime source changes.
Selection: verify referenced evidence and source/artifact hashes, SDK compatibility,
boot/tool input closure, local links, host/workflow/pin checks and simplicity hashes.
No unrelated native rerun is required for this documentation-only change.

Simplicity: choose a small index of existing sealed archives plus missing replay
support files instead of another SDK packaging framework or duplicate target
archives. This removes scattered intake instructions; no runtime path is retired.

## Qualified layers

| Workload | Producer evidence and expected result | Consumer status |
| --- | --- | --- |
| Startup | Existing startup/handler/mask coverage in the command-runner lineage; see the [native contract](../../NATIVE-SHELL-STARTUP.md). The original [startup packet](../shell-startup-2026-09-07/README.md) only covered DFL/IGN; it is not evidence of custom-handler support. | Independent later startup coverage is recorded by userland; require its exact receipt and source set for acceptance. |
| DASH-argv | [Final signal packet](../dash-consumer-signal-2026-09-13/README.md): actual dash launches unchanged helper, stdout `argv ok\n`, child/parent 0, backend 17 twice, six reclaims. Argument/environment corruption: helper 91/owner 2130; skipped helper: owner 2310. | New producer candidate; independent replay remains open. |
| DASH-signal-table | Same final packet: substitution transfers `USR1\n`, actual trap prints `signal ok\n`, child/parent 0, backend 17 twice, six reclaims. Dropped post: owner 2175; bypassed PID guard: parent signal 10/owner 2176. | New producer candidate; independent replay remains open. |
| DASH-syntax-error | [Syntax packet](../shell-syntax-execution-2026-09-09/README.md): unchanged `if then\n`, stdout empty, status 2, native diagnostic, four reclaims. Skipped main/close controls reject 1501/1503. | Userland independently consumed this workload in its `docs/evidence/dash-helper-consumer-2026-09-10/` packet. That historical acceptance does not qualify the latest source set. |

The final 287-case connections run covers arguments, signal-table and process/pipe
regressions. Startup/syntax are in **command-runner**, not that 287-case run.
Do not add the historical suites together and call them a matched phase-one run.
A fresh combined consumer qualification must run both suites on one frozen source
set; retain any failure before changing inputs.

## Integration boundary for UL-081 review

Consume the complete private fixture with its matching owner, startup envelopes,
rights, source pins and build recipes. Do not copy individual interposed functions
into the stock SDK. Upstream musl retains fork bookkeeping and signal internals;
the captured harness builds the private staging/rebind/exec/wait adapters.
`fork-client.c`, `exec-stage.h`, `shell-client.h` and `pipe-shell-client.h` own the
bounded fixture choreography. Rust dispatch/pipe owners enforce the matching
protocol. The fixed executable names are capability routes, not a filesystem.

The argument/signal environment is `WITNESS=value`, `LC_ALL=C`,
`PATH=/nonexistent`, plus granted `PWD=/work`. Captured `workloads.json` and source
pins are checked offline. The older argv packet's environment is superseded only
by the final signal packet; its sealed bytes remain unchanged.

Signal `kill` supports only the current positive PID with signal 0 or SIGUSR1.
Foreign PIDs reject EPERM; groups and other valid signals reject ENOTSUP; invalid
numbers reject EINVAL. Posting may enter the handler before returning. This is
not general POSIX kill, signal-aware waiting or cross-process signal authority.
Private copy/exec/pipe profiles have fixed images and bounded descriptor/child
lifetimes. General path/pointer handling, arbitrary pipelines and recovery cannot
be inferred from these fixtures. SDK owners must agree a supported integration
boundary before broader adoption; this document does not supply their sign-off.

## Replay intake

`inputs.json` pins the existing source, artifact and SDK archives and receipts.
`support.tar.gz` supplies the additional local boot/build/documentation files,
released offline standards and tool lock missing from the runtime source archive.
No large target archive is duplicated. Transfer the referenced archives with this
packet if replaying away from this checkout. Verify SHA-256 before extraction.
Extract only into fresh owned directories using a confined extractor; reject
absolute paths, traversal, special files and escaping links. The SDK contains an
internal relative Makefile symlink, which must remain confined to its root.

Restore the final signal packet's `sources.tar.gz` at the fresh Aether root,
then this packet's support archive at that same root. Restore the SDK archive into
a separate private directory. Use the captured tool lock and exact tool hashes;
path relocation must preserve tool bytes. Zig 0.16.0, Rust 1.98.0 and QEMU 11.1
remain external setup prerequisites, not bundled binaries. Boot inputs are
included for offline use; never silently fetch or update a pin during replay.

From that fresh Aether root, after creating `zig-out`, use the existing commands
with the restored SDK directory (the archive's `native-c-5olokhku` child):

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /absolute/private/sdk/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --command-runner \
  --libc-build /absolute/private/sdk/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Own each process group and impose the documented 300-second host and 1800-second
per-suite outer deadlines. The harness also bounds builds and individual guests.
Keep stdout/stderr, results.json, generated artifacts and all failed attempts in
fresh output roots. Do not rerun collectors into any sealed packet. Verify final
source hashes stayed frozen and independently inspect exact statuses, output,
EOF, acknowledgments and reclamation; exit zero alone is insufficient.

The first command-runner replay on these final inputs is **outstanding coverage**,
not a recorded success. If its independent consumer run exposes a compatibility
issue, preserve it and resolve that issue before marking phase one accepted.

## Remaining release work

Independent matched phase-one intake and UL-081 boundary review come first.
Then qualify unchanged wait, failed-exec, descriptor-closure/leak, redirection,
denied-redirection, pipeline, substitution and early-reader workloads with their
actual consumer helper and resource requirements. Full interruption/recovery,
persistent executable loading, OpenZFS, package management and sys-init assembly
remain separate release gates. This packet is an experimental replay handoff,
not a bootable general-purpose shell release.

## Local intake verification

PASS: all members of the final signal packet's seal verify, all 256 frozen
runtime/test sources match, and all 4,311 regular SDK archive files match the
qualified live SDK. The receipt, libc and tool-lock digests match the native report.
The archive retains a confined relative Makefile link; the live SDK uses an
absolute link to the same verified file. The separate musl-audit provenance tree
is retained in the original archive. Two collector assumptions about those
layouts failed before archive creation; both attempts are retained here.

The 346-file support archive was read back against its index. Restoring runtime
and support archives into a fresh owned source directory passes `zig build test`
in 6.23 seconds using the existing shared compiler caches. The working checkout's
host checks also pass. This is host replay, not a clean-cache build or a new
native/consumer qualification. No target archive was duplicated or old evidence
modified. Captured collectors are historical recipes; their fixed output names
must be changed before reuse, never run against this sealed packet.
