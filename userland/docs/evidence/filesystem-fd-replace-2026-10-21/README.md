# Chosen-target stream replacement — 2026-10-21

UL-007/081/082: `aefd_stream_replace` adds chosen-target stream redirection over
the canonical table and existing observed close. Distinct success resets only target
cloexec; self preserves flags. Known unconsumed error preserves state, consumed
terminal error leaves a target hole/source usable, unknown preserves metadata and
retires admission with no replay/publication. FILE source/target/self returns -38
before effects. This is not full atomic POSIX dup2, native grants or shell selection.
[Contract](../../proposals/FS-FD-REPLACE.md), [plan/review](review.md),
[final results](summary.json), [source candidate](candidate.json).

Actual Python3.10.21/3.14.7 final runs each pass19 replacement scenarios plus
unchanged22 creation/18 output/14 lifetime scenarios per C child and269 live C/Rust
file cases. Six compiling omissions fail exact C assertions plus observed failed
child; generic compiler/sanitizer/watchdog errors cannot satisfy controls. Strict
C17 warnings/format/UBSan and Rust2021/default Clippy/rustfmt/unsafe denial pass.
119 SDK headers and exact dependency/source/tool/resource/library/runtime/helper
closure pin before use and relevant inputs recheck afterward. No suppressions.

Actual host pipe-backed source/target streams prove bytes reach the replacement
and old target reaches EOF in both tag directions. A console tag is backed by a
host pipe here, not a native console. Empty/self/same-binding/full table, flags,
missing/stale/invalid inputs, FILE source/target/self rejection, known unconsumed
retry, consumed error/source survival and unknown with both actual states pass.
Explicit fixture cleanup closes unresolved endpoints and checks EBADF independently
of file-client abort. Close observations are injected; OS pipe/read/write/close
are real. The unchanged real Rust handler/process/AF07 file policy uses synthetic
storage over host pipes, not native OpenZFS or a linked shell.

Thirty-two-member source-only candidate:
`build/service-deliveries/filesystem-fd-replace-2026-10-21-v1`, manifest SHA256
`5b43ec90ed2481b618d0b23e4801b9dde18d5997bbcd319e611f984824cd7183`.
New source/tests and exact predecessor C/host sources, license, contract and dependency
receipt included; Rust dependency closures remain separately pinned. No native
SDK/engine copy, executable/profile activation or immutable prior packet changes.

[Retention](retention.json) inventories all three passing owned attempts in
[attempts.tar.xz](attempts.tar.xz), preserving commands/environment/deadlines,
streams/process cleanup, checker/source snapshots and binary hashes. Initial18-case
scope predates FILE self rejection and stronger actual post-error output checks;
final minimum/current runs use19 cases. A patch-context mismatch failed before
mutation, then corrected patch applied. Production implementation unchanged across
scope refinement; no failed qualification attempts. One streaming hash/size readback
verified every archive file before exact root removal:17,797,690 logical bytes
removed,3,512,184 archive bytes retained. Physical reclamation not measured.
Current Python lzma retention is separate from actual minimum qualification.

Quality logs, preserved-input verification and final source hashes accompany the
sealed evidence. Implementing-agent technical review only; independent owner/
reader pending. FILE/full source-backed replacement, native creator/read/write/
close adapters, selected mixed shell/startup/table, native copy/failed-exec parent/
FD state, immutable image authority, whole code/stack/heap/workspace/backing/channel
fit and matched dispatcher/readiness/shutdown/native command/error/cleanup/fresh
boot remain open. Full UL/M3/R1/POSIX/Zsh/packages/TTY incomplete. No sibling edit/
message, native guest, target installation, monitoring, SDK/default/limit/pin change.
