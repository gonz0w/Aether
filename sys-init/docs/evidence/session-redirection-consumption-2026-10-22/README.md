# Descriptor session and file-backed redirect consumer — 2026-10-22

[Decision0199](../../decisions/0199-session-redirection-consumption.md) consumes
41-member redirect and36-member session candidates with exact predecessor and
process15 dependencies:14 complete deliveries/354 member hashes verify before and
after use. C file client/facade/codec and Rust handler/process/service bytes stay
at earlier pins. The old92-file exchange packet/current source closure are checked
unchanged. There are no runtime source, accepted-owner/default/released-pin changes.

New tests/fd_dispatch_session.c uses actual session/redirect code over one borrowed
canonical map/client. Its host stream callbacks derive from decision0198 and use
actual OS pipes; unknown/known-refusal close observations are injected. Startup is
synthetic AEFDT001 with empty entries, not authenticated native startup. Invalid
startup/readmission reject before I/O. Pipe publication creates logical0/1 with
source selectors3/4; file open creates logical2 with FILE selector3. The server
includes the unchanged host App/fixture and new tests/native_fd_session_server.rs,
using unchanged Peer/actual handler/ProcessFiles/client/AF07 service with synthetic
storage. Fresh source builds, not captured-response replay or fake file RPCs.

Six paired live sessions pass client0/server0:

- Positive: eight file exchanges; duplicate-before-target-close redirects FILE2
  onto PIPE1, closes actual host writer and produces EOF at PIPE0. Reads through
  source/new alias share offsets (ab/cd/ef); current seek returns4. Exact AF07
  requests are lookup/read/read/read/close; source lookup1/local close1. Distinct
  target has cloexec0 while source stays1. Full and omit-cloexec128-byte snapshots
  decode correctly without map mutation or I/O; projection preserves the new alias
  and omits flagged pipe/source entries. Finish closes three logical entries,
  reports3 attempted/3 removed/0 remaining/unknown0 and both raw transport closes0.
- Known target refusal: actual remote duplicate is prepared, close returns-13
  unconsumed, map remains unchanged, unpublished duplicate is closed once. Direct
  remote selector4 probe returns-9, proving actual broker rollback. Original file
  still reads abc. Six file exchanges and exact source lookup/read/close; finish
  reports3/3/0/unknown0. Original target error is retained, cleanup status0.
- Lost duplicate header: server performs preparation but cannot deliver header.
  Receipt reports unresolved1/unknown1 with no named prepared selector, target
  attempt, cleanup or publication. Source lookup only; peer retires after second
  exchange fails. Retired finish reports0/0/3/unknown1 and first_error-5.
- Lost cleanup header: known target refusal follows real preparation; server closes
  the temporary descriptor but loses its reply. Receipt preserves target-13,
  cleanup-5, prepared selector4 and unresolved1/unknown1. Source lookup only; no
  cleanup retry. Retired finish reports0/0/3/unknown1.
- Unknown target close, with and without physical close: preparation succeeds,
  target completion becomes unknown. Map stays unchanged; receipt preserves
  prepared selector4/unresolved1/unknown1, no rollback attempt or publication.
  Source lookup only; server observes EOF, retires source, repeats serve as Closed.
  Retired finish reports0/0/3/unknown1; it makes no further adapter/I/O calls.

All cases preserve caller short-read tails or dirty output on failed operations,
clear private workspace, retain both actual raw local transport closes0 exactly
once, reject post-finish/readmission and cache identical receipt fields without
repeating cleanup. Owner explicitly closes unresolved physical stream ends;
actual physical-close count2 is checked separately from local receipts. Retired
metadata with remaining3 is not native settlement. All successful server cases
join service fixture threads and source-local close count1 is observed.

Three omissions strictly compile and fail specific C assertions: omitted prepared
close ->33 (rolled-back FD probe); publish after target error ->31; hide unresolved
allocation after lost dup ->34. Corresponding server exits101/101/0 cannot satisfy
these C oracles. All18 owned processes across nine paired sessions stop without
forced cleanup. Actual commands, cases, artifacts and exact source/tool/header/
runtime/library identities are in preparation.json. No failing preparation run.

Strict C17 diagnostics/UBSan/format and Rust2024/default Clippy/rustfmt pass.
107 host C inputs/headers pin after preprocessing but before compilation and
recheck afterwards. LLVM resource headers, UBSan and38 Rust host/compiler libraries
pin before builds and recheck along with tools and sources. Compiler60s/4MiB and
paired-session30s watchdog/owned process group cleanup apply. Wrappers and runner
are inert reproduction text; use new private output/evidence roots for reproduction.

This is host integration with synthetic storage, not a native executable/IPC,
actual console, OpenZFS-backed shell, native copy/immutable exec/failed-exec,
POSIX dup2 or complete code/stack/heap/workspace/backing/channel fit witness.
No target objects or guests are run; producer's individual-frame/object evidence
is not promoted to sys-init native fit. Selected linked shell/startup/authenticated
native adapters/copy/exec/placement remain required before full sys-init dispatcher/
readiness/shutdown and Aether exact native command/error/cleanup/fresh boot.
[Current handoff](../../FILESYSTEM-BOOT-HANDOFF.md#session-and-file-redirection-checkpoint--2026-10-22).
No sibling edits/messages, new shared ABI/exception/quota/default/pin or release
promotion. Independent affected-owner/reader/native acceptance stays open.
local-checks.json records full offline checks; sha256.json seals all packet files
except itself. Earlier evidence remains immutable.
