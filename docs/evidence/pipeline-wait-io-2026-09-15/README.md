# Parent wait alongside child I/O — 2026-09-15

The private capacity dispatcher now retains one authenticated parent wait while
child I/O continues. It receives32-byte requests incrementally, validates PID and
options, observes only scoped native child handles, and returns to the I/O loop
when a blocking wait is pending. A selected terminal is collected once when the
reply is constructed; the reply survives partial7-byte sends without reapplying
collection. One offset serves the mutually exclusive read/reply phases.

The first blocking wait must be observed against a live child before initial child
I/O is enabled. This proves overlap rather than merely collecting after all I/O.
Parent uses blocking waitpid/wait4 and final exhausted wait3; all three specific
results and unchanged ECHILD status are checked. Dispatch returns only after all
children finish and four replies are delivered with all three collected bits set.
Premature parent termination rejects while replies remain; the enclosing owner
checks final parent status before reclaim as before.

The mutant completes a live blocking wait with zero. Parent121 then owner2750
must reject before reclaim; timeout or unrelated failure is not acceptance. Positive
retains exact input/EOF, pipes/stdout, diagnostics,12 admissions with per-slot
counts3/3/0/3/3 and15 normal terminals/reclaims over3 generations.

## Size and implementation

A shared bounded transfer loop replaces duplicate synchronous receive/send loops
used by setup. Wrappers keep borrowed storage alive, and direction controls the
native operation. Counts are checked against the requested chunk before advancing
the pointer and remaining length. Existing timeout/backpressure and error codes
remain; no dynamic memory, new syscall, authority table or service is introduced.
The retained wait is generation-local with a32-byte frame and bounded scalar state.

Final positive/mutant owners are16360/16312 bytes, within the unchanged16384 limit.
All builds retain rustc1.98 opt-level=s, fat LTO and existing panic/target/link flags.
Source ELF is254680 bytes.39/74 previous top-level ELF/raw images are identical;
35 owner binaries change due to shared transfer generation and are requalified.
All prior client images are identical. Five private runtime files change among281
inputs: owner.rs, pipes.rs, copies.rs, live-worker.c and pipeline_capacity.py.
Kernel, shared adapter/pipe core, SDK, sibling repositories and released pins stay
unchanged.

## Attempts and reproduction

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`

Attempts1,2,7 failed at the existing size linker guard before running native cases.
Attempts3–6 and8–10 are link-only probes, also over budget. Each has its source
snapshot and applicable logs/maps/command receipt; attempt2 includes its size map
inside its artifact archive. These are build/resource failures, not timeouts or
native runtime failures. Host checks passed on attempts1,2,7 and final sources.
The opt-level=z experiment made size worse and was reverted; dispatcher/replacement
outlining and slot-width experiments were not retained. See triage.json and the
preimplementation review/follow-ups in NATIVE-SHELL-STARTUP. Final size-probe files
record the successful exact-source link, separate from native qualification.

Runtime/review archives bind sources and guidance. collect.py archives and verifies
all generated files for every suite attempt before deleting only owned duplicates.
All failed probes remain in this packet. SHA256SUMS covers all members except itself.
No older sealed packet is modified.

## Remaining work

This is a bounded private wait/I/O witness, not general exec multiplexing or full
dash. Exec/readiness and parent descriptor closure remain setup phases. The new
handler's wider WNOHANG/denial/interruption schedules need direct qualification;
older profiles retain their existing tests but do not qualify this new state machine.
Unchanged pipeline/early-reader scripts, SIGPIPE/status composition, real dash
main/eval, console/TTY, full matching suites and independent SDK/userland intake
remain open. Persistent OpenZFS, packages, recovery and sys-init assembly remain
R1 work. No bootable-shell release claim.

Final qualification: attempt11 passes all51 native cases and104 host checks on281
frozen runtime inputs. All35 changed previous owners are requalified. Native case
time totals 142.603 seconds; kernel mapping remains 8007680 bytes. Source/replacement maps
76/74 of128 pages. No native runtime failures occurred; ten earlier build/size
attempts are preserved. Final checks cover formats, workflow, pins, simplicity,
whitespace and frozen source/archive integrity. Full matching runner/connections
suites were not rerun for this private capacity change and remain a handoff gate.
