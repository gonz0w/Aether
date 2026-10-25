# Descriptor integration batch — 2026-10-21

UL-007/081/082 groups startup, a single operations surface, flags/seek, inert export
and terminal finish reporting over the existing canonical map/client. No second
FD ledger, native capability or default shell selection. [Contract](../../proposals/FS-FD-SESSION.md),
[plan/review](review.md), [final results](summary.json), [candidate](candidate.json).

Actual Python3.10.21/3.14.7 final runs each pass:

- 15 integrated startup/pipeline/query/export/finish scenarios per C child;
- 73 unchanged host scenarios (19 replacement,22 creation,18 output,14 lifetime);
- 269 live C/Rust file cases through the same map/client, now with session views
  for file open/dup/seek/flags/close;
- eight assertion-specific compiling fault controls, plus strict C17 diagnostics/
  format/UBSan and Rust2021/default Clippy/rustfmt/unsafe checks.

Startup failure/readmission publishes nothing. Full and omit-cloexec exports
roundtrip without source effects and cannot hide invalid duplicate FILE entries.
Shutdown exercises known unconsumed/consumed errors, unknown with both physical
states, missing closer, retained descriptors, cached receipt and both raw negative
transport closes. Host pipe byte/EOF/EBADF and explicit cleanup complement injected
source observations. Real Rust handler/process/AF07 storage is synthetic; this is
not native console/OpenZFS execution or POSIX conformance. FILE/full replacement
remains unsupported. Projection/receipt cannot confer copy/exec/cleanup authority.

Separate target build: eight strict freestanding C17/-O2 x86_64-unknown-none ELF
objects and relocatable link,217 header hashes pinned before use/rechecked after,
123 host SDK headers likewise. Explicit header-only input is the existing local
native-service-runtime-2026-10-06-v2 musl SDK stage; no selected SDK pin changes.
All internal C symbols resolve. Remaining memcmp/memcpy/memmove/memset imports are
explicit libc requirements; memmove is compiler-generated in existing fd-client.
Forty-one static frame reports have maximum264 bytes per function, excluding call
chains/callbacks/libc/interrupts and total resource fit. No executable, loader,
Aether native ABI/runtime or kernel-stack acceptance follows from these builds.

Thirty-six-member source-only candidate:
`build/service-deliveries/filesystem-fd-session-2026-10-21-v1`, manifest SHA256
`7aa7a9c15d12f83a9c76655397557cf1f0aed48191becd9ce884bc9bd701131d`.
New session implementation/header/tests plus exact prior sources, contract/license/
dependency receipt and native-header identities; no SDK/engine copy or native
executable. Rust closures separately pinned. All prior packets remain immutable.

[Retention](retention.json) inventories six owned attempts in
[attempts.tar.xz](attempts.tar.xz), preserving exact commands/environment/deadlines,
streams/process cleanup, source/checker snapshots and artifacts. First failure:
formatted mutation target did not match after passing live baseline. Second:
host/six controls and target compiles/link passed but import expectation omitted
compiler-generated memmove. Checker corrected; no production workaround or warning
suppression. Two earlier minimum/current six-control passes retained. Final two
runs add saved-field receipt/cache and stream-seek controls (eight), avoiding a
padding-sensitive/self-comparing oracle. Live file seek also routes via session.

Every archive member hash/size verified in one streaming readback before exact root
removal:38,277,956 logical bytes removed,7,169,124 archive bytes retained. Physical
reclamation not measured. Current Python lzma retention is separate from minimum
qualification. Quality logs, input-preservation and final source receipts accompany
the sealed record. README/architecture intros consolidate repeated small-helper
progress; original module contracts/evidence remain linked and unchanged.

Sys-init decision0198 has independently consumed the preceding32-member mixed
helpers on host. It has not selected this new session or a native shell. Actual
technical review here is implementing agent only; independent owner/reader pending.
Next source-backed FILE/full replacement, authenticated native stream adapters and
coherent linked-shell/startup selection; immutable executable/copy/failed-exec
preservation, complete code/stack/heap/workspace/backing/channel fit and matched
dispatcher/readiness/shutdown/native command/error/cleanup/fresh boot remain open.
Full UL/M3/R1/POSIX/Zsh/packages/TTY incomplete. No sibling edit/message, native guest,
real installation, background monitoring, SDK/default/limit/release-pin change.
