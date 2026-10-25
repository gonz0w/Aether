# UL-082 transport change review — 2026-10-19

Requirement: add a bounded service request loop over retained native channel
bindings, preserving existing one-write policy and C/SPA ownership. Current Aether
receipts supersede the old callback/recovery blocker; they are producer evidence,
not independent acceptance here. inputs.json freezes the inspected handoff,
channel code, current build guards, receipts and tools before implementation.

Scope: new private AFSRPC01 framing, one provisioned connection, readiness reply,
lookup/read/write/stat/close/disconnect, partial-frame rejection, lost-reply
retirement and endpoint cleanup. No client-supplied peer/session/backend object,
UTC, attachment or rights escalation. Owner is consumed by the loop; every exit
revokes references and consumes its backend before endpoint closure. Each frame
is64 bytes, payload16, at most64 requests, bounded100000 transfer polls/frame;
existing native endpoint holder enforcement remains required. No new grants,
threads, allocation, async runtime, transaction capacity or real-prefix install.

Applicable: Foundations O-01–05/I-01–08/E-01–08; Distribution applicability
FS/SV/B; approved TD/TC/TE, CR/CP and adopted SE-01–05. Existing readonly machine
wire/SDK/boot markers and sealed bridge delivery remain unchanged. New code is
BSD-2-Clause; native channel entry borrows the pinned Aether synchronous trap
idea. Shared UTC and original engine remain separately owned dependencies.

Tests planned before implementation: typed host success with exact greeting,
alias data/EOF and reply progress; malformed/stale/foreign handles/rights/version;
every frame split and partial EOF, receive/send/close errors, response loss after
write, one provider call/no replay, request exhaustion, exactly-once backend drop
before both endpoint closes. Rust2021 no_std, warnings denied, unsafe forbidden in
wire/loop; narrow native FFI with panic=abort, explicit safety and no Send/Sync.
Pinned rustfmt/default Clippy; native x86_64 object generation/link inspection.
Owned commands60s, host tests30s, quality180s with bounded child commands.
All attempts and source/tool/argv/environment/output/cleanup receipts retained.
Changed sources invalidate affected tests; no periodic job or release claim.

Independent native launch/authority and full engine recovery remain NOT RUN for
this new composition. Current producer build explicitly rejects writable+IPC and
accepts only the old probe callback. Do not edit siblings or bypass that guard;
deliver exact service inputs and an owner proposal after local checks. No human
or affected-owner review is invented; reader remains deferred. UL-082 stays active.

Simplicity: (1) direct calls are simpler, but cannot exercise authenticated request
delivery or reply-loss retirement. (2) choose a single synchronous bounded client
using the existing native channel mechanism; defer multiple-client scheduling,
general uptime and new mutations. (3) remove no historical evidence or compatible
path now: old readonly and write-probe fixtures retain separate consumers.

Actual results and technical assessment are appended after testing.


## Actual technical assessment and disposition

FST-01–11 and FSE-01–04 (summary.json maps stable IDs to exact test functions)
pass on actual Python3.10.21 and3.14.7, including the Rust-entry/typed-C provider
path with injected host transport. Seven compiling mutants are rejected by test
assertions. Both final runs reproduce native object SHA256
`dab564abbcc70ca93cebec7fec8d6017c569367dde8419abbf2d2701401150b1`.
Warnings/unsafe-op diagnostics, Rustfmt/default Clippy, native panic-abort build,
ELF/symbol and C ABI/packed controls pass. Final quality (all three published pins
plus adopted draft checks), both actual interpreter syntax and whitespace pass.
The old18-member bridge seal/members remain exact. New25-member candidate seal is
`5dd5f492dd2ab2c57321a8fd610f1f6fa488dece4c4b40466a37236bf24144c4`.

Technical review by this implementing Codex agent: traced trusted provisioning,
no request-selected principal/context/UTC, monotonic local tokens and handle
attenuation; all transfer outcomes, explicit committed/unknown stop, preserved
progress on response loss, one-write no-replay budget, and shutdown before both
close attempts. No Send/Sync or allocator was added. C ABI fields are explicit;
unsafe storage/SPA/dataset/trap obligations remain caller contracts. Test-only
injected traps are cfg(test), absent from delivered native code. No suppression.
This is self-review, not independent owner/reader approval. Those remain pending.

Three failed host attempts retained: test-discovery expectation mismatch, mutant
compile warning, host panic-strategy incompatibility. Early complete local source
snapshots were absent; retained hashes/logs cannot reconstruct every early build.
Final runs snapshot exact local sources; native candidate bytes match both final
interpreters. Dynamically loaded host libraries/system SDK are not a complete
hermetic dependency closure. Native sanitizer, kernel holder enforcement, whole
stack/peak memory and actual original-engine service run remain unqualified.
No native test was attempted, failed or retried in this change.

Aether's current exclusive profile guard is exercised directly from its pinned
AST: writable bridge+IPC rejects before an import/build. The current accepted
intake pins the previous probe seal/entry. The exact new owner proposal is ready;
selecting/provisioning that matched profile is an Aether-owned integration change,
not authority to change sibling implementation here. Do not bypass it with a
local kernel/init fork or falsely claim a relocatable object is launchable.
UL-082 remains active; next matching owner profile/client/native cleanup/recovery,
independent intake, then sys-init executable assembly. Continuous observer lifetime,
new mutations/POSIX and persistent runner/packages/Zsh/ISO/M3/R1 remain open.

Postflight: full mutable owner-builder hash drift was detected and retained in postflight.json. Current source adds an independent lifetimes mutation selector/hook/label routing. The service-exclusion guard AST is byte-for-byte structurally equal and its actual rejection is re-exercised; probe intake and current STATE stay exact. No silent repin or native attempt; original inputs/candidate remain unchanged.
