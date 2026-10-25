# UL-082 authorized metadata service review — 2026-10-21

Requirement: bind the qualified original-engine metadata getter to authenticated
service handles, with an explicit new protocol, before persistent package/shell
assembly. Current Aether writable IPC, executable and bounded sys-init activation
gates are cleared in producer receipts. No independent acceptance is inferred.
inputs.json freezes current producer/local inputs and verifies all old delivery
members before implementation. Preserve the borrowed metadata.rs binding bytes.

Scope: separately selected fs_metadata/AFSRPC07, inheriting AF06 operations and
limits, plus opcode12 on a retained handle. New METADATA16 right is explicit and
attenuated; LOOKUP/READ/WRITE/MUTATE_DIR do not imply it. Trusted provisioning may
delegate it, never UID/GID/mode labels. Owner resolves peer/session/handle before
the backend. Metadata includes raw64-bit labels/mode/flags/links, signed seconds
and checked nanoseconds; the112-byte wire omits backend object/generation/parent
identities. No POSIX narrowing, credential inference, chmod/chown or promotion.

Reuse the current serialized owner, bridge and bulk scratch. Unsafe metadata
borrows remain inside the exclusively owned ZPL backend, with SPA retained and no
mutation/export/property/teardown overlap. Clear output on failure. Malformed or
contradictory metadata retires all aliases/context; known engine errors publish
no body. Loss of header/either body frame ends the connection without replay.
Endpoint closure, engine export and native reclaim remain separate obligations.
No allocation, threads, new grants, observer/transaction/history/quota increase,
new guest allowance or default/sealed AF06 mutation. Backend support defaults to
explicit unsupported error, never successful fabricated metadata.

Plan: policy/typed-C/wire host tests of rights, foreign/stale handles, malformed
identity/kind/size/times, high owner labels, signed times/special bits, provider
error/partial copy, exact complete/zero-padded body, all reply-loss boundaries,
once-only context-before-endpoint cleanup and no mutation/retry. Compiling
omission controls, Rustfmt/default Clippy/warnings, safe policy, native panic-abort
object/import/ABI checks. Regress AF06 against the current separately pinned
baseline; never call changed source old native qualification. Commands owned and
bounded60s (host tests30s), quality180s with bounded children. Exact sources/tools/
argv/environment/logs/results retained including failures; compact readback before
generated-output removal. Changed inputs invalidate affected evidence.

Applicable Foundations O/I/E, Distribution FS/SV/PX applicability, approved
TD/TC/TE and CR/CP, adopted SE-01–05. BSD-2-Clause original additions; preserve
engine/Rust/musl notices. No shared standard/pin changes or sibling edits/messages.
Actual native service metadata selection, fit, authorized-handle/negative/recovery
witness and launchable replacement need matched Aether intake; no permission to
bypass its sealed profile. Independent owner/reader review stays pending.

Simplicity: raw direct getter calls are simpler but cannot enforce retained-client
authority. Reuse AF06's synchronous owner/framing with one new operation and
cfg-isolated backend method; do not build another service/runtime. Remove none of
the old selected paths now because their immutable consumers remain supported.
Keep the borrowed binding intact rather than duplicate its validation/type ABI.

Results, findings and completion limits follow after checks. UL-082 stays active.


## Actual results and self-review

FSM-01–08 in summary.json map the eight metadata behaviors to exact named tests.
All23 actual-entry host tests pass on actual Python3.10.21 and3.14.7, including
15 inherited directory behaviors and coherent file/parent metadata after a real
C-fixture create/write. Eight compiling omissions fail test assertions as intended.
The C observer checks context retirement before malformed-result error transfer;
test assertions run after the FFI call, avoiding unwind through the C boundary.
The borrowed metadata.rs source remains exact. No lint suppression was added.
Rustfmt/default Clippy, safe policy/service compilation, panic-abort no_std native
object/import and C signature/layout/packed controls pass. Both final interpreters
produce the same object SHA256
`b5729862346409392064045af6f953484d3d6fbf9cad2b279840907003222f7b`.

The current AF06 checker separately passes15 entry tests/27 compiling omissions,
activation/counter/legacy controls. All older sealed member hashes match; this
is current host compatibility, not old-source/native/LTO bit identity. Its run
preceded the final metadata-only test/recipe additions; those cfg-excluded tests
and new recipe do not alter AF06 production code or invalidate those assertions.
Pinned host C UBSan also passes all23 cases, with no diagnostic; it instruments
the C fixture only. Rust/native sanitization remains absent. Actual minimum/
current Python syntax, quality/all released pins/adopted snapshots and whitespace
pass. A separate whole-stack/native service fit/original-engine metadata RPC
witness remains required; do not reuse the READ-only binding witness as that run.

Technical self-review by implementing Codex agent traced retained principal/handle
resolution before backend, explicit rights attenuation, exclusive context/SPA
borrow through getter, copied-only result, invariant/size validation and all-exit
cleanup. Raw labels/signed seconds are endian-explicit with no narrowing and no
object/generation/parent export. Every header/body reply prefix stops without
replay; provider/malformed errors publish no body, and malformed completion closes
context before transfer. Default support is explicit unsupported95, not no-op.
Independent affected-owner/reader approval remains pending; no sign-off invented.

Five failed preparation attempts are retained: omitted transitive header, missing
test import, default Clippy chunk recommendation, incomplete array adaptation,
and stale C-fault observation across serial test setups (host abort). The fixture
monitor/reset repair and final controls exercise that boundary. Initial input
manifest is reconstructed exactly against its original retained digest in
input-versions/; subsequent source snapshots/commands/logs stay intact. Earlier
passing native objects were path-dependent; the final recipe reads the same
source-pinned maintained paths and proves exact end hashes. No old receipts were
rewritten; no native failure, guest or retry occurred in this work.

New77-member sealed review input:
`build/service-deliveries/filesystem-service-metadata-2026-10-21-v1`, seal
`98a9fd12db4ecd1c736fe3ce332c9b69c631e043d4d87313827145675ba230a8`.
It is a relocatable object/source/notice/input packet, not a standalone executable
or hermetic/independent rebuild. Next matched AF07 Aether intake/provider/client,
full native authority/negative/recovery/fit, replacement Rust launch owner and
sys-init consumption; exact contract is FS-SERVICE-METADATA. No sibling edits or
messages, default/pin/limit/history/observer reset or reused120s idle allowance.
UL-082 stays active. Mode/promotion, ABI29 shell/PID/FD, filesystem-backed runner/
loader, packages, Zsh/TTY/ISO/R1 and independent reviews remain open.

Retention: all6660 compact source/command/output/result records were hash-read back before disposing only14 newly owned generated roots.1601 generated binaries/rlibs/objects total223690529 logical bytes were removed; physical/net disk savings were not measured. New77-member AF07 candidate, old deliveries, frozen engine baseline and active30-member executable remain retained and verified. Final source/binding/candidate/evidence readback passes.
