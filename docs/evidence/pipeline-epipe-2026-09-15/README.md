# Native early-reader EPIPE — 2026-09-15

The private two-pipe native dispatcher now retains and forwards signed EPIPE
replies with zero payload through its fragmented transport. A final reader either
closes without reading or exits with its reader still held. After observed native
terminal and holder cleanup the relay's write to Second fails with EPIPE. The
relay checks ten exact First bytes, closes both held ends and exits. After its
terminal the original writer retries First, receives EPIPE and closes normally.

Each schedule requires ten successful write/read bytes on First, none on Second,
one EPIPE per pipe, no EOF reads, three generations and fifteen normal exits/reclaims.
Frames, holders and FIFO state must be retired before reuse. Owner scheduling
forces these boundaries for the test; it is not a production scheduling policy.

## Results and attempts

`python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
passes all fourteen native cases on 273 frozen inputs. Final target case time is
36.750 seconds. Existing eleven capacity/dispatch/stop cases
retain their exact outcomes. New pipe-early-reader and pipe-early-exit pass.
The pipe-wrong-errno mutant replaces -32 with -5 in an otherwise valid error reply;
actual relay exit97 must precede owner2726 with zero reclaims.

Attempt1 passes thirteen cases and reaches the exact expected mutant behavior,
but fails its ordered-context oracle because the harness mistakenly listed owner
before worker. This is a harness assertion defect, not an accepted negative test.
Its sources, log, incomplete report and artifacts are retained. Attempt2 changes
only that order and passes the complete suite. Runtime sources are identical
between attempts. No timeout or unrelated panic is accepted as a negative result.

`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
returns0 on both source snapshots; final host.log records all 104 host checks
passing. Final checks also verify pinned Rust/C formatting, workflow, standards,
experience, simplicity manifest and four members, whitespace and frozen inputs.
This selected suite covers the affected private profile; full matching old
connections/runner and independent consumer qualification remain handoff gates.

## Compatibility and scope

Only pipeline_capacity.py, native-capacity/pipes.rs and worker.c change among the
273 runtime inputs. Base capacity worker/owner remain byte-identical. The pipe
worker now preserves negative errno after rejecting nonzero error payload; dispatch
owners retain/count errors independently from successful effects. Compatibility
hashes and changed inputs are recorded. Largest owner is 8288 bytes, below
16384; no kernel, shared pipe-core, SDK, dependency, authority, resource-limit,
sibling repository or released pin changes. No new unsafe boundary is added.

This qualifies raw pipe errno, not SIGPIPE delivery or actual dash fork/exec.
Seven-binding integration, unchanged consumer scripts, matching full suites and
independent intake remain next. Filesystem, packages and sys-init assembly are
still needed for R1. No full-shell or release-readiness claim follows.

The preimplementation review is in NATIVE-SHELL-STARTUP. Source archives preserve
both attempts; review-inputs binds local documentation/test support. Target reports
retain commands, timestamps, tools/SDK identity, envelopes, ISOs and serial hashes.
collect.py archives and verifies every generated file against its original before
removing only this run's two private output roots; cleanup.json is the receipt.
Prior sealed evidence is unchanged. SHA256SUMS covers this packet except itself.
