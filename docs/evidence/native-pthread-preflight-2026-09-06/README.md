# Actual pthread creation preflight — 2026-09-06

The experimental conformance port source-rebuilds musl 1.2.6 pthread_create with a
recorded signal-mask query before first-thread setup. Aether does not yet support
that operation. The actual function now returns ENOSYS before modifying libc state,
allocating stack storage or attempting clone. Upstream ignores later mask-call
errors; this guard makes the presently unsupported path fail closed. It is not
successful pthread creation or a production userland adoption.

The fixture checks two calls, unchanged output handle, errno, TLS sentinel,
libc flags/thread-list/count, memory quota and absence of a native child. Positive
and supervised replacement cases pass in both memory profiles. Disabling the guard
rejects at exact assertion 181, rather than a timeout. Existing signal operations
remain unsupported; a future successful query alone would not establish all later
signal, clone or lifecycle requirements.

## Verification

Final results and exact commands are in [final/results.json](final/results.json);
source bytes are frozen in final/sources.tar.gz with hashes checked before and
after every command. Six new target cases plus 110 older thread cases pass.
Host checks pass 97 Python tests, Zig tests, offline standards and workflow checks;
pinned C/Zig formatting passes. No kernel changed, as checked against the retained
native-indefinite-wait qualification. Unchanged memory/image/M4 suites were not rerun.

Run python3 scripts/thread_smoke.py --pthread-preflight with explicit --libc-build
and --tools-lock arguments from the final command record, then repeat with --large.
The supplied strict libc build and verified musl archive are prerequisites.

## Source and attempt retention

Source verification checks original bytes against the verified archive, the exact
pthread patch, original/adapted manifests and linked identities. Only the rebuilt
pthread source and disposable architecture syscall header differ. The libc archive
is unchanged. COPYRIGHT and original source are retained with the source archive.
The probe uses actual libc memory routines and the existing startup I/O hook;
it does not install VM lock stubs. Upstream-only warning exceptions and header
ordering are documented in docs/NATIVE-C.md. Disassembly and tool/ELF identities
are retained here.

All attempts remain in target-attempts.tar.gz, inventoried by target-directories.json.
Initial attempts 1–3 failed compilation on private-header/macro/upstream-warning
integration; attempt 4 failed linking on duplicate __mmap from fixture and archive.
Attempt 5 linked but the loader rejected the absent TLS segment. The fixture now
links only probe plus pthread object and supplies an explicit checked TLS sentinel.
Attempt 6 passed all three cases. Final qualification follows those corrections.
These failures are not counted as passing target runs. SHA256SUMS covers the packet.

## Remaining work

Actual pthread start/exit/join, signal semantics, cancellation, repeated creation
and resource budgets remain open. No companion acceptance, independent review,
optimized target coverage, stress or release readiness is claimed. The persistent
filesystem and assembled shell/package release still require further integration.
