# Actual dash builtin in a copied child — 2026-09-15

The forked writer now executes pinned dash printfcmd/flushall without replacing
its image. The private owner skips only writer replacement; relay and reader keep
checked denied/retried exec and CLOEXEC commit. Copy readiness, dispatch release,
scoped wait and native cleanup remain. The writer checks copied TLS identity,
closes its inherited capture and unused reader, redirects the live pipe writer to
stdout, then explicitly probes its former capture reference for EACCES. It consumes
inherited stdin/EOF, emits its diagnostic byte and closes all remaining descriptors.

A literal builtin argument cursor is initialized in the copied image. This calls
real pinned dash code but not main, parser or evaluator. Arbitrary inherited dash
state, builtin error/signals and unchanged scripts are not established. The owner
still performs sequential replacement/readiness, release, I/O and wait phases;
general execution/data/wait scheduling is next. No new kernel or shared SDK ABI,
transport, pipe state table or service is introduced.

## Oracles and resources

Positive requires exactly12 image admissions:3 each for parent/peer/relay/reader,
zero for the copied writer. Copying does not count as image admission. All15 normal
terminals/reclaims, exact pipe/stdout bytes, inherited input/EOF, diagnostics and
holder closure remain required across3 generations. Wrong first byte must reject
relay111 then owner2726 before reclaim. A successful builtin return alone cannot
satisfy the test.

The new source ELF is255048 bytes; both new owners16296 bytes remain below16384.
All66 prior top-level ELF/raw images are byte-identical. Only live-worker.c,
copies.rs and pipeline_capacity.py change among281 frozen runtime inputs.
All32 existing dash object hashes are verified before linking and recorded in the
receipt. Original objects, licenses and public musl fork source are preserved;
release pins and sibling repositories are unchanged.

## Reproduction

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`

Preimplementation review/outcome is in NATIVE-SHELL-STARTUP. Frozen runtime and
review archives retain inputs and guidance. Target receipts retain commands,
SDK/tool identities, timestamps and artifact/serial hashes. collect.py verifies
all generated files against an archive before removing only owned duplicates.
SHA256SUMS covers every packet member except itself; previous evidence is immutable.

Unchanged pipeline/early-reader scripts, SIGPIPE/status composition, signal
interruption, console/TTY, matching full suites and independent SDK/userland intake
remain separate gates. Persistent OpenZFS, packages, recovery and sys-init assembly
remain R1 work. No full-dash or bootable-shell release claim.

Qualification: all47 native cases and104 host checks pass on281 frozen inputs.
No failed attempts occurred; intentional rejection evidence is retained. Target
case time totals 128.403 seconds; kernel mapping remains 8007680 bytes. Source images use
76 of128 mapped pages, with52 remaining; copied writer keeps that mapping and the
replacement relay/reader use25 pages. These are mapped-page counts, not peak memory.
Final format, workflow, pin, simplicity, whitespace and frozen-input checks pass.
Full matching runner/connections suites were not rerun for this private capacity
change and remain a future handoff gate.
