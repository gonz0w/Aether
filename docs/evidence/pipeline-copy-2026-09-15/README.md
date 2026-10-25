# Native copied pipeline participants — 2026-09-15

A private AENMX004 variant now creates the writer, relay and reader using the
existing native freeze/copy primitive, instead of three separate image admissions.
Parent slot0 sends a bounded seven-binding snapshot including a CLOEXEC alias at
FD10, then freezes. The owner drains exactly64 bytes, observes the exact native
freeze sequence, validates expected records/counts against live parent holdings,
and stages both pipe objects before copying. A stale copy sequence rejects first;
the valid sequence then succeeds with the same previously unconsumed channels.
Child readiness completes the staged transition before pipe use.

Each child checks native PID/parent, copied TLS and the retained CLOEXEC alias,
rejects old parent channel grants and uses explicit new grant registers. Volatile
child TLS/stack writes are checked against the unchanged parent's values after
all child readiness. Children close unused inherited endpoints; ten exact bytes
and one EOF traverse each pipe. Three lifetimes require six image admissions,
nine copies and fifteen normal exits/reclaims. Stale handles, channel exhaustion
and generation retirement remain checked.

## Qualification

`python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
passes all sixteen native cases on 274 frozen inputs. Target cases total
42.711 seconds. New pipe-copy passes; pipe-bad-snapshot deliberately
understates the FD3/FD10 alias count and rejects owner2731 before any native copy
or reclaim. Fourteen preceding cases retain exact positive/negative meanings.
There were no failed attempts. Intentional rejection logs are preserved.

`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
returns0; host.log records all104 host checks passing. final-checks records pinned
Rust1.98 edition2024 and Clang-format21.1.8, standards/experience/workflow checks,
simplicity manifest and four members, whitespace and frozen source verification.
Old profile full connections/runner reruns and independent SDK/userland acceptance
remain required before a new handoff; this is selected private-profile coverage.

All 15 preceding top-level ELF/raw images are byte-identical (compatibility.json).
The new positive owner is9424 bytes, below16384. No kernel, shared pipe modules,
SDK, dependency, quota, sibling repository or released standards pin changes.
The existing kernel's copy budget and per-domain authority checks are reused.
The C freeze assembly names all result/grant registers and a memory clobber;
stack/TLS bytes are copied privately, and parent capabilities are not inherited
as native authority. Source hashes and exact build flags are retained.

## Limits and next work

This uses an authenticated fixture descriptor snapshot, not installed libc FDs
or the actual dash fork adapter. It does not qualify replacement-image exec,
CLOEXEC removal at exec, libc rebind, SIGPIPE or unchanged consumer pipelines.
Those and failed/ambiguous admission cleanup precede matching full suites and
independent consumer intake. Filesystem/OpenZFS, packages and sys-init assembly
remain R1 work. There is no full-shell handoff or release-readiness claim.

The preimplementation review is in NATIVE-SHELL-STARTUP. final-sources preserves
all inputs; review-inputs preserves current local guidance and host test support.
The target report binds tools/SDK, commands, timestamps, envelopes, ISOs and serial
hashes. collect.py archives and verifies every generated file against its original
before removing only this attempt's private output root; cleanup.json records it.
Prior sealed packets are unchanged. SHA256SUMS covers this packet except itself.
