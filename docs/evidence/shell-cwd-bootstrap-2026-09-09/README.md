# Directory bootstrap rejection

All 323 command cases and host/pin/workflow checks (98 Python tests) pass on final
frozen sources. Four added cases reject a directory reference aliased to stdin,
a final directory record truncated at 16 bytes, a v2 header received by the v3
selection, and a v3 header received by the v2 selection. Each requires client110,
unpublished startup state, no client I/O and two generations/four reclaims.

Version senders send only their header and close the writer. The truncated sender
closes after the half record. Cleanup accounts for that consumed endpoint and
reclaims both service/client domains. The existing bounded half-frame send loop
is shared with metadata truncation; its existing negative cases also pass. No
C decoder/adapter, kernel, upstream object, sibling, SDK default or pin changed.

No failed or interrupted attempts occurred in this step. Earlier attempts remain
in the unchanged predecessor packet. The collector checks its manifest, verifies
final source hashes and the simplicity snapshot, and reads back all archived
source/target members. qualification.json names the run/counts; manifest.json seals
this packet recursively. No fresh M4 run for these sender/harness-only changes.

Commands from repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 docs/evidence/shell-cwd-bootstrap-2026-09-09/collect.py
```

See the [pre-code selection](../../NATIVE-SHELL-STARTUP.md#directory-bootstrap-rejection-selection--2026-09-09).
Next: directory reply corruption/truncation and poisoned-connection teardown,
then identity/PWD mismatch controls. V1/V3 and other bootstrap truncation points
remain unqualified. This is not a complete directory handoff, full shell or
persistent filesystem. Consumer acceptance and release gates remain open.
