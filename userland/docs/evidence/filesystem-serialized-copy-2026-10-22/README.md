# Serialized file inheritance v1 qualification — 2026-10-22

UL-007/081/082. [Contract](../../proposals/FS-SERIALIZED-COPY.md),
[implementation review](review.md) and docs/quality/change-review.md bind scope.
The additive copy_inherit_serialized_v1 API holds one exclusive file-ledger borrow
across preflight, trusted native-copy callback and local binding clone. The old
inherited_child frozen-parent precondition remains unchanged. No native operation,
wire, extra persistent state/ledger/allocator/handle or sibling change is supplied.

26 process-profile host tests:18 retained and eight new actual-library cases,
ten compiling semantic omission controls (eight retained/two new). Shared offsets,
independent flags/last close, queued parent close/reopen, thirteen FD capacity/all
three children, invalid/busy/stale preflight no callback, confirmed refusal preserving
state/history, unknown retirement/no replay, mismatched confirmed child, unwind
retirement pass. Tests use the existing actual Rust AF07 service/Owner with
synthetic storage and scripted native observations. An actual failed safe-Rust
callback reentry compilation proves exclusive borrow enforcement, not native
stream synchronization. Final external host/target consumer builds exercise public
type visibility. Strict Rust2021/rustfmt/default Clippy/unsafe denial; generic
x86_64-unknown-none library generation is not native execution/resource fit.

Initial minimum/current passes exposed only internal-library usage; source review
then found missing re-exports of new callback/result types. Added public exports
and external no_std consumer checks and requalified final sources on both actual
interpreters. Initial and final attempts retained separately, without hiding the
coverage gap. No old evidence/candidate bytes rewritten. Checker/source/tool/input
hashes, exact argv/environment/bounds/process-cleanup and raw logs remain retained.

This supplies the userland-owned local ordering alternative requested by sys-init
Decision0201/BG-069. The owner must still enforce sole-source and stream admission
exclusion, authenticate frozen snapshots/tokens/copy outcomes, settle native child
obligations, agree versioned staging and implement child-only context/TLS/auxv/
channel/file-generation/history transition. No affected-owner sign-off is invented.
BG-070 full transaction/link/whole fit/native positive/refusal/unknown/continued-
parent/readiness/wait/cleanup remains open. Full shell still lacks fork stage;
prior exact link evidence is reused unchanged, not replayed by this library test.
Immutable exec/public dup2/full UL/M3/R1 and independent reader remain open.

Source-only handoff: `build/service-deliveries/filesystem-serialized-copy-2026-10-22-v1`, 17 members; manifest SHA256
`01c185942e5449c9e2dadbe825f48642bcd81e4635ad63c19b0c75e1e7446d6a`. Contains predecessor process-source closure with exact
qualified maintained inputs, checker, new/local process contracts and dependency/
license receipts. The checker snapshot requires maintained repository layout and
pinned offline dependencies. This does not select an owner/native runtime.

All four exact owned attempts archived and streaming hash/size checked before
removal. Logical bytes removed 105,954,688; archive bytes
retained 25,568,128. Physical reclamation not measured.
Current Python/lzma is retention-only, separate from minimum-version qualification.
Final verification receipts accompany the seal. No sibling edits/messages, guest,
install, quota/default/pin change or monitoring. Independent owner/reader pending.
