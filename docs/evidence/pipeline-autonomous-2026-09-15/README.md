# Pipeline child I/O without dispatch release — 2026-09-15

Copied builtin and replacement relay/reader now start their existing bounded I/O
protocol after readiness, without reading an additional dispatch-release token.
The owner omits those child sends. Parent and capacity peer retain their release;
parent early WNOHANG, sequential exec, parent closure and dispatch phases remain.
Requests can queue while peers replace; bounded FIFO backpressure is unchanged.
This removes a child scheduling dependency, not the whole sequential dispatcher.

The positive requires exact inherited input/EOF, pipe/stdout bytes, diagnostics,
closed holdings and15 normal terminals/reclaims over3 generations. Exactly12 image
admissions with per-slot counts3/3/0/3/3 exclude copied writer replacement. The
negative owner sends the obsolete byte only to the writer. Its first close reply
must be rejected: writer129 then owner2726 before reclaim. A timeout cannot pass.

## Resources and compatibility

Both new owners remain16296 bytes within16384. Source ELF254856 bytes; replacement
ELF248632 bytes reuses the pinned dash-linked client (relay/reader do not call its
writer builtin branch). The same32 upstream objects remain hash-checked, with
original provenance/notices. No dependency pin, kernel, shared adapter, SDK,
capability limit or sibling repository changes.

68/70 previous top-level ELF/raw images are identical. The two copied-builtin
source images change because the optional token read is separated from the TLS
check; both are requalified. All previous owners and replacement images remain
identical. Four private runtime files change among281 frozen inputs: owner.rs,
live-worker.c, libc-worker.c and pipeline_capacity.py.

## Reproduction and limits

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`

Preimplementation review is in NATIVE-SHELL-STARTUP. Runtime/review archives bind
inputs and guidance; target receipts retain commands, tool/SDK identities, case
timestamps, artifacts and serial hashes. collect.py verifies every file against
its archive before removing only owned duplicates. Prior evidence stays unchanged.
SHA256SUMS covers every member except itself.

Interleaving parent waits and I/O, general execution scheduling, real dash main/eval,
unchanged pipeline/early-reader scripts, SIGPIPE/status composition, interruption,
console/TTY and independent SDK/userland intake remain open. Full matching suites
remain a handoff gate. Persistence/OpenZFS, native packages, recovery and sys-init
assembly remain R1 work. No full-dash or bootable-shell release claim.

Qualification: all49 native cases and104 host checks pass on281 frozen inputs.
No failed attempts occurred. Intentional rejection evidence is retained. Native
case time totals 135.435 seconds; kernel mapping remains 8007680 bytes. Source maps76/128
pages; replacement maps74/128. These are mapped-page counts, not peak memory.
Final checks cover formats, workflow, pins, simplicity snapshot, whitespace and
frozen input/archive integrity. Full runner/connections suites were not rerun for
this private capacity change; they remain a matching handoff gate.
