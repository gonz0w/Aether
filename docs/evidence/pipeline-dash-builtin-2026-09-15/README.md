# Actual dash builtin through the pipeline — 2026-09-15

The private replacement writer now invokes pinned dash0.5.13.5 printfcmd and
flushall through its granted pipe descriptor. Literal argv storage and the builtin
argument cursor are explicit; the existing stdin read/EOF check remains separate.
Relay and final reader retain actual musl I/O. Exact output, EOF, three diagnostic
bytes, holder closure and fifteen normal reclaims remain independently required.
The negative case changes the builtin format's first byte: relay111 then owner2726
must reject before reclaim. Successful builtin return alone cannot pass the test.

The harness verifies all32 existing dash objects before linking, records their
hashes and wraps main to the fixture entry. No replacement implementation of printf,
new dependency pin, service or authority path is introduced. Original upstream
objects and COPYING.dash remain unchanged and are retained in the source archive.
Only libc-worker.c and pipeline_capacity.py change among281 runtime inputs.

## Scope and resources

This runs a real builtin in a replacement worker, not an in-place copied child.
It does not invoke dash main, parse a shell script or establish initialized shell
state, signal/error paths or complete builtin semantics. Executing builtins directly
in copied children and coordinating execution/data/wait remain next. Owner phases
are sequential; unchanged pipeline/early-reader scripts, SIGPIPE/status composition,
console/TTY, full matching suites and independent SDK/userland acceptance remain.
Persistence/OpenZFS, packages, recovery and sys-init assembly remain R1 requirements.
This is not a full-dash handoff or bootable-shell release.

New positive client ELF is248664 bytes. Both new owners remain16360 bytes within
the existing16384-byte ceiling, identical to the preceding positive exec-request
owner. All62 preceding top-level ELF/raw images are byte-identical. Native loader,
channel/FD limits, kernel, shared adapters, SDK, siblings and released pins are
unchanged. No owner-budget simplification was required for this bounded client step;
the24-byte remaining headroom still constrains scheduling integration.

## Reproduction and evidence

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`

Preimplementation review is in NATIVE-SHELL-STARTUP. Runtime and review archives
retain exact inputs and guidance; target receipts record tools, SDK identity,
commands, case timestamps, serial hashes and artifacts. collect.py verifies every
file against its archive before deleting this run's owned duplicates. SHA256SUMS
covers all packet members except itself. No prior evidence is modified.

Qualification: all45 native cases and104 host checks pass on281 frozen runtime
inputs. No failed attempts occurred. Intentional rejection evidence is retained.
Target case time totals 123.762 seconds; kernel mapping remains 8007680 bytes.
Each dash replacement uses74 of128 mapped pages (54 remaining); ELF size is not
peak memory or TCB size. All previous image bytes are unchanged. Final checks cover
formatters, workflow, released pins, simplicity snapshot, whitespace and frozen
runtime/archive integrity. General matching runner/connections suites were not
rerun for this private client/harness-only change and remain a future handoff gate.
