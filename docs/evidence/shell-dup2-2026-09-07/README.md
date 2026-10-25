# Shell descriptor replacement — 2026-09-07

All 226 native command-runner cases and 98 host tests pass.

This producer prerequisite adds dup2 to the existing single-context startup facade.
It does not deliver full dash or close UL-007. Userland's twelve candidate scripts
and their original expected outputs/helper are captured under consumer/ with exact
hashes; all twelve actual native shell workloads remain NOT RUN.

The native positive case saves/replaces/restores stdout, rejects invalid or closed
sources without disturbing targets, preserves self-dup CLOEXEC, replaces the final
stderr alias and performs replacement with all sixteen slots occupied. Real input
is copied through the restored output binding. Independent owner checks require
exact contents, all final remote closes, two fresh generations and four reclaims.

Three deliberate implementations fail at exact oracles:

| Control | Client terminal | Owner rejection |
| --- | --- | --- |
| Clear self-dup flags | 70 | 1501 |
| Preserve CLOEXEC on distinct replacement | 71 | 1501 |
| Skip displaced alias release | 0 | 1503 |

The final control is essential: a successful client exit cannot hide a remote
ownership leak. These intentional failures stop at the rejection; they are not
normal cleanup witnesses. The positive case must independently complete cleanup.
No flags, references or authority are transferred to another process by dup2.

The host close-boundary probe uses the exact copied startup_io/dup2 functions with
a mocked remote close. Consumed EIO allows replacement, unknown EIO rejects without
publication, and unexpected close failure rejects. A mutant that drops the poison
check fails specifically at `unknown close rejection`. This is local host algorithm
evidence, not new native transport-error qualification. Existing native transport
controls are included in the complete command-runner regression.

## Reproduction and retained inputs

Use the same explicit read-only SDK/tool lock as the startup handoff:

```sh
python3 scripts/launch_smoke.py --command-runner \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The target receipt binds source bytes, SDK archive and tool identities, exact
compiler/link/boot commands and raw results. execution-context.json records the
output-directory creation time; the unchanged harness lacks per-case start/end
timestamps, so this packet does not claim full draft evidence-field coverage.
sources.tar.gz retains the producer
sources; target-artifacts.tar.gz retains the entire qualified suite. collect.py
checks frozen source hashes and every archive member. The unchanged SDK's original
retained startup/SI-06 archive remains the prerequisite; this packet neither edits
nor republishes it. A private rebuild must use matching sources and SDK, not a
mutable sibling checkout. The duplicate positive envelope/ISO/log are convenience
artifacts, not an assembled release image or new full-dash delivery.

check-close.py retains host commands, compiler identity, source/binary hashes and
exact control outputs. These evidence recipes operate on fresh packet copies when
reproducing; do not overwrite sealed evidence. C formatting uses pinned Clang-format
21.1.8 and the approved local configuration. Host/pin/workflow checks and source
syntax/links are recorded. Kernel, loader and native ABI are unchanged, so unrelated
QEMU profiles are not rerun. Independent consumer acceptance remains theirs.

An initial SDK inventory check compared all bytes successfully but asserted 4,311
as the whole archive count. The archive also contains the upstream musl tarball,
for 4,312 regular files total. sdk-check-attempt-1.json retains that analysis
failure; check-sdk.py separately verifies 4,311 SDK files and one source archive.
No compiler, target or SDK input was changed to correct the count.

Next is checked custom-handler/mask behavior for actual dash initialization, then
child creation/exec/wait and pipe/file redirection with scoped in-memory backing
and explicitly granted helper images. Full dash requires those stages and matching
userland execution; OpenZFS is not a prerequisite for this bounded integration.
