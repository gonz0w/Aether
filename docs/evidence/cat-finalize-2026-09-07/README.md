# EINTR and completed finalization re-entry — 2026-09-07

The producer conformance client now has explicit EINTR and completed-cleanup
re-entry witnesses. No Toybox image, callback or stdio flush is executed here.
The owner returns complete EINTR at the existing partial-progress error points;
the client must observe musl errno EINTR, stop data requests and close all roles.

| Interrupted operation | Status | Input consumed / stdout / diagnostic bytes |
| --- | --- | --- |
| Read | 1 | 11 / 11 / 0 |
| Write | 1 | 22 / 11 / 0 |
| Diagnostic write | 64 | 0 / 0 / 16 |

Each sink is checked against the exact fixture prefix; input storage is unchanged.
Retry-write and force-success mutants require owner1530/1501. Wrong errno returns
client114, which cannot satisfy the terminal oracle. This injects a complete errno
reply, not a POSIX signal or an ambiguous partially committed request.

The private `finish_bindings` helper caches its completed result. The fixture calls
it again with a different status after successful copy0, usage64, acknowledged
input-close error1 and poisoned-read1. It must retain the first result, send no
channel trap and leave every local binding retired. Resetting the completion guard
must produce client113/owner1501. This proves completed re-entry only, not recursive
in-progress callbacks or concurrent invocation. The helper is not a published
userland API and cannot substitute for Toybox's own callback/flush/exit integration.

All existing owner alias checks, exact backend bytes, terminal EOF, backend stale
denial and four native reclaims over two generations remain. No kernel primitive,
authority, resource limit or dependency changed. See [pre-code contract](contract.md)
and [native reference](../../NATIVE-CAT.md#eintr-and-completed-finalization-re-entry).

## Reproduction

Run `python3 scripts/launch_smoke.py --command-runner` with
`--libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and
`--tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Use `--connections` and `--inherited-launch` with the same SDK/lock for regressions.
Host: `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.
Scoped Clang21/Rust2024 formatting and workflow checks accompany the runs. The
shared transport header retains legacy formatting for opt-in trap counters.

## Limits

Abnormal-stop supervision, actual native Toybox/SDK initialization and finalization,
independent consumer pin/build and CAT acceptance remain open. No assembled R1
readiness follows. Release pins, prior UL-059 bundle and siblings are unchanged.
Run UTC boundaries are retained; per-case timing, independent review and extended
coverage remain unavailable.

## Qualification

All first attempts pass: 203 command cases (193 prior plus ten new), six
connections and nine inherited-launch cases. All 98 Python host tests, Zig tests,
offline pins, workflow and scoped formatting checks pass. All three final receipts
match frozen runtime sources. The 34 kernel/build inputs and SDK/libc/tool-lock
identities match the preceding unknown-reply qualification. Largest new owner is
5,928/8,192 bytes; no limit increased. No failed attempt was observed or discarded.

final-artifacts.tar.gz retains frozen sources, compiled clients/backends, argument
artifacts, native envelopes and raw logs. ISOs, duplicate installed boot files and
kernel.elf are omitted with identities in retained receipts. Archived sources and
argument bytes are independently rechecked. Qualification/timing files and manifest
bind this evidence. Prior UL-059 bundle artifacts remain byte-identical.
