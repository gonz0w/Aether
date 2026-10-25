# Direct wait dispatcher intake — 2026-09-15

The native parent now exercises the wait/I/O state machine directly: unrelated
peer PID returns ECHILD, live wait-any and specific-child WNOHANG return zero, and
all three preserve the status sentinel. These initial probes leave child I/O held.
The first live blocking wait enables I/O, retaining the prior overlap requirement.
Blocking wait3/waitpid/wait4 then collect three distinct authorized child PIDs in
any completion order. A repeated wait on the first collected PID returns ECHILD;
final wait-any exhaustion does likewise. Every reply traverses partial7-byte sends.

The dispatcher keeps its single pending frame, shared read/reply offset and
once-only collection bits. This profile expects eight replies; the prior four-reply
profile remains. Initial terminal selection is forbidden, and initial nonblocking
or denied requests do not enable child I/O. Numeric PIDs still select only the
parent's granted child handles. Wrong denial errno and omitted collection bits
must each reject parent131 then owner2750 before reclaim. Exact streams,12 scoped
admissions and15 normal reclaims remain required over3 generations.

## Scope and compatibility

The positive and wrong-errno owners are16328 bytes; omitted-collection owner16312,
all within16384. Source ELF254968 bytes.75/77 prior top-level ELF/raw images are
identical; only the two prior wait/I/O owners change with the initial probe gate
and are requalified. All previous client images are unchanged. Three private
runtime files change among281 inputs: pipes.rs, live-worker.c and pipeline_capacity.py.
No compiler flags, kernel, shared adapter/pipe core, SDK, sibling or released pin
changes. No new syscall, dynamic memory, service or capability mechanism.

This qualifies direct wait-any, WNOHANG, scoped denial, once-only collection and
complete partial replies for the bounded fixture. It does not establish interrupted
wait cleanup, lost-reply recovery, arbitrary schedules, general exec multiplexing
or full dash. Parent/peer release, exec/readiness and parent close remain setup
phases. Real dash main/eval, unchanged pipeline/early-reader workloads,
SIGPIPE/status composition, console/TTY, matching full suites and independent
SDK/userland acceptance remain. Persistent OpenZFS, packages, recovery and sys-init
assembly remain R1 work. No bootable-shell release claim.

## Reproduction and evidence

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`

Attempt1 stopped before native cases due to a malformed Python startswith call in
case selection. Its sources, passing host checks and build artifacts are retained.
The corrected prefix covers the existing family without a second positional
argument. This was a harness failure, not a target failure or passing negative test.

Preimplementation review/outcome is in NATIVE-SHELL-STARTUP. Runtime/review archives
bind inputs and guidance; reports retain commands, tools/SDK identities, timestamps
and native artifact/serial hashes. collect.py verifies every file against its
archive before removing only owned duplicates. All attempts remain. SHA256SUMS
covers all packet members except itself; prior sealed evidence is unchanged.

Final qualification: attempt2 passes all54 native cases and104 host checks on281
frozen inputs. Both prior changed wait/I/O owners are requalified. Native case time
totals 152.224 seconds; kernel mapping remains 8007680 bytes. Native source/replacement
mapping remains76/74 of128 pages. The sole failed attempt was the retained harness
error; no native runtime failures occurred. Final checks cover format, workflow,
pins, simplicity, whitespace and frozen source/archive integrity. Full matching
runner/connections suites were not rerun for this private capacity change and
remain required for a full handoff.
