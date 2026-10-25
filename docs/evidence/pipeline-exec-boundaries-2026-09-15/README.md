# Exec transaction boundaries for dispatch — 2026-09-15

The private replacement routine now separates three bounded transaction steps from
blocking channel and readiness handling: descriptor-table validation into caller-
owned filtered storage; admission for an observed frozen child; and descriptor
ledger commit followed by native publication. These functions stay in copies.rs
and introduce no new service, state object or public interface.

The existing routine still receives/authenticates requests and snapshots, observes
freeze, invokes admission, preserves the stop-after-admission cancellation point,
commits/publishes, sends tables/grants and observes readiness. The stop-during-table
control remains after publication. Denied-image receipts, stale-publication denial,
CLOEXEC comparison, standard-stream holding changes and final readiness checks are
unchanged. Arguments remain valid through synchronous native admission; the kernel
copies them before the helper returns. Caller-owned snapshot/filter storage stays
live through cancellation and table publication.

This is preparation for exec/I/O multiplexing, not its completion. Calling the old
blocking routine from dispatch would stall I/O; duplicating its transaction checks
would create competing authority paths. The extracted functions can be used by
incremental transport progression without either shortcut. Actual dispatch
integration remains next.

## Compatibility and resources

Only copies.rs changes among281 runtime inputs.43/81 previous top-level ELF/raw
images are identical;38 exec-owner binaries change and require native requalification.
Every prior client image is unchanged. All owners remain at or below16376 bytes
within16384; the probed wait/I/O owner is16360 bytes. Compiler settings, native
quotas, kernel, shared pipe core/adapters, SDK, sibling repositories and released
pins remain unchanged. No new unsafe primitive, allocation or dependency.

## Attempts and reproduction

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`

Attempt1 hit the unchanged linker size guard before native cases; its host checks
passed. Attempts2/3 are link-only probes, over the limit at16424/16408 bytes, with
maps, command receipts and sources retained. Final helpers fill caller-owned
storage and remain out of line. This supersedes the initial all-inline assumption;
no checks or cancellation points were removed to fit the limit. The final probe
fits; native qualification is recorded separately below.

Preimplementation review/follow-up is in NATIVE-SHELL-STARTUP. Runtime/review
archives bind sources and guidance; receipts retain commands, SDK/tool identities,
timestamps, artifacts and serial hashes. collect.py verifies every generated file
against its archive before removing only owned duplicates. All failed attempts
remain, including standalone probes. SHA256SUMS covers every member except itself.
Prior evidence is immutable.

Nonblocking exec progression, interrupted/lost-reply wait recovery, actual dash
main/eval, unchanged pipeline/early-reader workloads, SIGPIPE/status composition,
console/TTY, matching full suites and independent SDK/userland acceptance remain.
Persistent OpenZFS, packages, recovery and sys-init assembly remain R1 work. No
full-dash or bootable-shell release claim.

Final qualification: attempt4 passes all54 native cases and104 host checks on281
frozen inputs. All38 changed owners are requalified. Native case time totals
151.640 seconds; kernel mapping remains 8007680 bytes. Three size-limit attempts/probes
are retained; none ran native cases. No native runtime failures occurred. Final
checks cover formatting, workflow, pins, simplicity, whitespace and frozen-source/
archive integrity. Full matching runner/connections suites were not rerun for
this private owner refactor and remain a handoff gate.
