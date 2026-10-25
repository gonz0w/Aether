# File operations in one tagged table — 2026-10-21

UL-007/081/082: [file table helpers](../../proposals/FS-FD-TABLE.md) now implement
logical open/dup/seek/close/cloexec in the same map used by tagged reads. Logical
slots and remote selectors are independent; pipe/console occupancy stays intact.
Source-confirmed success publishes new entries or close/flag updates; errors and
unknown completion preserve prior map. A retired client prevents reuse. Unknown
open/dup may have remote effects; preserving local bytes is not rollback.

Actual Python3.10.21/3.14.7 each pass269 live C/Rust host cases/six compiling
semantic omissions, C17 strict diagnostics/format/UBSan and Rust2021/default
Clippy/rustfmt/warnings/unsafe denial. Actual new C operations/read dispatch use
real Rust wire/process/AF07 service over host OS pipes with synthetic storage.
No native streams, startup/shell selection, object/ELF link, concrete memory fit,
trap/OpenZFS/runtime or immutable exec acceptance. Stream mutations return -38.

The eighteen-member source-only candidate at
`build/service-deliveries/filesystem-fd-table-2026-10-21-v1` has manifest seal
`fe10be587ff93896cf66198d679a94c7d745ec18076369cd05ead01825e021ea`.
It includes new helpers/host harness, exact C dependencies/codec/map/fixture,
license/contract/dependency pins. Rust libraries remain separately pinned; no new
SDK/live engine/selected native payload copy or accepted sys-init API.

Cases comprise13 scenarios and256 incomplete mutation-header replies (each0..63
prefix of open/dup/close/cloexec). Scenarios exercise pipe3 versus file3, logical5/6
versus source3/4, signed current/end seek, shared offsets/final close, independent
flags, logical0 file and checked zero read, local-full open AND dup, remote13-file
limit, missing/stale-source errors, semantic read denial then healthy read, stale
map generation, conflicting positive selector and AF07 body/count/close failures.
Request/lookup/read/final-close counters, unchanged map/caller guards, denied replay,
observed child exit, source thread join and one backend drop are independent oracles.
All source flags/FD lifetime claims remain bounded host policy, not native exec.

Compiling controls require specific C assertions plus Rust failed-child observation:
aliasing without actual duplicate; selector uniqueness omission; omitted known-close
clear; clearing on error; omitted flag commit; logical index used as source selector.
Generic compile/sanitizer/watchdog/Rust error cannot pass. Complete routing16/
bindings6/facade12/client9/wire20/service77 source pins, Clang/Rust tools/native
libraries/LLVM resource headers,105-header C SDK closure, UBSan runtime and owned
helper verify before consumption; source/header/runtime recheck. Compile60s/live30s,
16MiB streams, clean environment/private owned group with complete child cleanup.

All six owned qualification runs pass: initial268-case current/minimum before
logical seek;268-case current/minimum after seek; final269-case current/minimum
with the local-dup-full boundary. Earlier stages are retained, not silently replaced.
All intentional failing controls and raw sources/checkers/argv/environment/logs/
binaries/cleanup receipts are recoverable in the verified archive. Each regular
file hash/size was streamed back before exact redundant root removal; byte totals
are in retention.json. Physical reclamation was not measured. No failed setup/
baseline attempts occurred. Final summary selects all current source changes.

[Review](review.md), summary.json, candidate.json, final-source.json, quality streams
and SHA256SUMS bind scope/identity. Previous source/evidence/standards/wire/SDK/default
pins and native limits remain immutable. No siblings edited/messaged, guests, real
install or full UL/M3/R1 acceptance. Local quality is structural/pin validation;
independent owner/reader and full source/native/publication gates remain open.

C callers must supply decoded canonical table, actual source binding, valid disjoint
ranges and exclusive stable/nonreentrant access; no arbitrary map mutation or client
reinitialization is safe recovery. Stream entries need an actual coordinated owner.
Next select/reconcile mixed shell startup/profile with native stream adapters and
mutations, native copy/failed-exec preservation, immutable executable admission,
whole code/stack/heap/workspace/backing/channel fit, complete sys-init dispatcher/
readiness/shutdown and native command/error/cleanup/fresh boot. Packages/Zsh/TTY open.
