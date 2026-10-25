# UL-007/081/082 file mutations in the tagged table

Pre-code scope: add open/duplicate/close/cloexec for file entries in the existing
proposed tagged map, without a second FD ledger. Logical allocation0–15 differs
from remote selector3–15. Stream slots are occupied and preserved; stream mutations
are explicitly unsupported -38. Sys-init decision0197 still requires selected
mixed startup; no owner agreement/default/native profile is inferred.

Map must come from successful decode, remain canonical and be exclusively managed
through coordinated helpers. Reuse existing selected lookup/shape/native-source
facade; do not duplicate FD service, allocator or stream policy. Fresh generation/
live-client check before effects; serial/nonreentrant C access, valid disjoint
ranges. Find a free logical slot before remote open/dup, no remote effect on local
full. Duplicate chooses lowest remote minimum3 separately from requested logical
minimum. Flags0/1 validated. Publish new slot only after complete successful source
reply and unused remote selector; conflicting positive selector retires source,
leaves map unchanged and never closes the already occupied selector as rollback.

Close/flags update only after actual confirmed source success. Known negative
result preserves table; unknown/retired client also preserves occupied metadata,
closes admission and requires external reconciliation. No false cleanup, new native
authority/settlement, successful stream no-op, libc symbol or exec implementation.
Open may use logical0 if empty; no fixed number implies class. No new4KiB runtime
array; mutable map replaces an eventual old table rather than duplicating it.

Host live C/Rust harness: actual new mutations and tagged reads to unchanged
facade/client/wire/ProcessFiles/sealed AF07 service, synthetic storage. Verify pipe3/
file3 collision, shared alias position/final close, flag publication, empty0, local
full before I/O, remote13-file exhaustion, known error/table preservation, stale
generation, duplicate positive selector and every0..63 partial reply for open/dup/
close/flags. Actual AF07 body/count/close faults retained. No native copy/fork/exec,
startup selection, streams/pipe mutation, object/link/full-fit or shell claim.

Pin routing16/bindings6/facade12/client9/wire20/service77 plus tools/libraries/
resource/header/runtime/helper before use. C17 strict diagnostics/format/UBSan and
Rust2021/default Clippy/rustfmt/unsafe denial. Minimum/current Python, owned60s
compile/30s suite/16MiB streams/clean group cleanup. Compiling omissions require
specific C assertions plus failed observed child, not generic infra failure.
Retain all attempts, run quality/syntax/whitespace, update canonical follow-ons.

Simpler alternative: add local aliases to the same remote selector or assume local
FD equals remote FD. Insufficient: first loses final-close ownership, second collides
with pipe/console. Reuse actual remote dup/close/flags and map slots, not a new object
store or transaction framework. Remove no accepted legacy path now; eventual runtime
must replace it explicitly. Independent owner/reader and full UL/M3/R1 remain open.

Scope extension before final qualification: expose logical file seek through the
same source-class lookup, so the current file API need not bypass the map for
position changes. No map mutation or new protocol is introduced. Test current/end
signed seeks with preserved shared offset; streams remain explicitly unsupported.

## Implementing-agent final assessment

The API mutates the same canonical map used by read lookup; no extra live ledger.
Ready checks enforce live client/exact map generation. Selected file lookup uses
existing class validation and returns -38 for streams. Free logical slots are
chosen before source open/dup; logical minimum is independent of remote minimum3.
Positive source selectors are range/uniqueness checked before local publication.
A duplicate selector is never closed as rollback; file admission retires with map
unchanged. No integer identity or metadata grants native rights.

Actual remote duplication owns shared offset/final-close semantics. Close/flags
commit only on complete zero result. Source errors preserve map; unknown effects
retain prior metadata behind a retired client and cannot be retried. Unknown
open/dup may allocate remotely without local publication, so unchanged map is
explicitly not rollback or proof of no source effects. Native endpoint/process/
source reconciliation remains external; local file close is not stream cleanup,
revocation/detach/device quiescence or successful supervisor shutdown.

Logical seek forwards through the same class/source mapping with checked whence
and existing signed64 codec; position stays source-owned and map unchanged. Slots
remain canonical after coordinated helpers; callers must start from successful
decode and preserve exclusive stable/nonreentrant access/valid disjoint ranges.
Arbitrary map mutation, concurrent occupancy changes, client reinitialization or
unreconciled startup state do not satisfy this contract. Existing constants/bounds
and predecessor source/wire bytes remain unchanged. No automatic4KiB runtime array.

Final minimum3.10.21/current3.14.7 each qualify identical sources/checker:269 live
host C/Rust cases/six compiling assertion-specific omissions. Source-backed local
and remote capacity, source/flag/lifetime failure preservation, logical0/selector
collision, signed/shared offsets and all256 partial mutation headers pass. The
local dup-full boundary checks client sequence and server request count to prove
no source duplicate was sent. Source thread join, C child wait, once-only local
close and backend drop complete. Strict C17/UBSan/format and Rust2021/default
Clippy/rustfmt/warnings/unsafe denial pass;105 SDK headers/source/tool/resource/
runtime pins verify before use and recheck. No suppressions or native campaigns.

Initial two passing268-case runs precede logical seek; next two passing268-case
runs add seek; final two269-case runs add local dup-full coverage. All six are
preserved with exact checker/source/log/binary/argv/environment/cleanup records.
No setup/baseline failure occurred; intentional failing controls remain visible.
Every regular file hash/size was read back in one streaming archive pass before
removing exact roots:28679013 logical bytes removed,6178820 archive bytes retained.
Physical reclamation not measured. No unrelated roots removed. Selected source/
contract and prior candidate/evidence/member seals verify unchanged. Final quality,
syntax and scoped whitespace pass; full audit/runtime/reader/publication NOT RUN.

Canonical contract/architecture/acceptance/backlog/current evidence and contributor
coverage/review/output scope updated; intent unchanged. Implementing-agent technical
review only. Independent owner/reader, reconciled selected mixed shell/startup,
actual stream adapters/mutations, native copy/failed-exec parent/FD preservation,
immutable executable admission, whole workspace/code/stack/heap/backing/channel
fit and complete sys-init dispatcher/native command/error/cleanup/fresh boot remain
open. No siblings/messages, new guests, install, pin/default/limit/wire changes or
full UL-007/081/082/M3/R1 acceptance.
