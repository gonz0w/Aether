# Tagged stream output — 2026-10-21

UL-007/081/082: opt-in `aefd_routed_write` stages const input in the existing
workspace and dispatches console/pipe output by explicit kind/selector. Read-only
file entries reject -30 without fallback. Known short/zero/error results return
unchanged; unknown/invalid results retire file admission once, never replay.
[Contract](../../proposals/FS-FD-WRITE.md), [plan/review](review.md),
[results](summary.json), [source candidate receipt](candidate.json).

Actual Python3.10.21 and3.14.7 each pass eighteen output scenarios plus fourteen
unchanged stream-lifetime scenarios per live C child and269 real C/Rust file cases.
Six compiling omissions require specific C assertions and observed C-child failure;
compiler/sanitizer/watchdog failures cannot substitute. Strict C17 warnings/format/
UBSan and Rust2021/default Clippy/rustfmt/unsafe checks pass.111 host SDK headers
plus exact source/tool/resource/library/runtime closure are pinned and rechecked.

Actual host pipe write/readback/EOF/close/EBADF checks are distinct from injected
completion/error observations. Cases cover short/full4096/zero writes, known-error
continuation, unknown with and without physical bytes, malformed/count/errno,
readonly files including zero, missing adapter/FD, stale identity, input bounds
and console-tag dispatch into a host pipe. No native console claim. Input/map
remain unchanged; staged source bytes/workspace clearing and no unknown replay
are checked. Unknown is not proof of zero effect or successful stream cleanup.

The exact predecessor stream/table/routing/file fixtures remain unchanged. Real
Rust handler/process/AF07 policy uses synthetic storage over actual host pipes.
No native SDK/engine copy, object/link/runtime qualification, source-grant change,
selected shell/startup or implicit consuming-owner acceptance. Original APIs and
all immutable packets/release pins/machine markers/limits stay fixed.

Twenty-four-member source-only candidate:
`build/service-deliveries/filesystem-fd-write-2026-10-21-v1`, manifest SHA256
`4213eb0244501c77f8993b63915c00cfabc33dce7390d07dc3dcedff2c862941`.
Rust dependencies remain separately pinned. Actual new source/tests, exact prior
C/host sources, contract, license and dependency receipt are included.

[Retention](retention.json) inventories all three passing attempts in
[attempts.tar.xz](attempts.tar.xz), with raw argv, clean environment, deadline,
process cleanup receipt, stdout/stderr, checker/source snapshots and artifact hashes.
The first passing scope lacked explicit healthy-error continuation and used a broad
stale-branch omission. Final fixture adds continuation and uses precise missing-
stale-retirement control to avoid uncertain binding use in the faulty variant.
Production implementation unchanged. Final results select minimum/current reruns.
No failed qualification attempts. Every archive file hash/size was verified in one
streaming readback before removing the exact three owned roots:15,821,002 logical
bytes removed,3,262,536 archive bytes retained. Physical reclamation not measured.
Retention uses current Python lzma, separately from minimum-version qualification.

Local quality outputs, preserved-input receipt and final source hashes accompany
the sealed record. Implementing-agent technical review only; independent owner/
reader, native stream adapters and pipe creation, selected shell/table/startup,
native copy/failed-exec preservation, immutable image authority, full code/stack/
heap/workspace/backing/channel fit, dispatcher/readiness/shutdown and fresh matched
native commands/errors/cleanup/boot remain open. Full UL/M3/R1/POSIX/Zsh/TTY/package
acceptance remains incomplete. No sibling edit/message, new guest, target install,
background monitoring or native readiness implied.
