# UL-082 AF07 operational owner review — 2026-10-21

Requirement: consume the qualified AF07 service in a separately selected Rust
operational owner. Aether now reports all selected positive/transport/context/
metadata-loss/provider gates passing. The approved four-provider batch is consumed;
its earlier timeout remains unexplained and no new guest authority follows.
Pin receipts/handoff and engine ABI before implementation (inputs.json). Preserve
the77-member AF07 service and existing AF06 owner/executable/seals unchanged.

Scope: separate launch-metadata-owner.rs calls aether_fs_metadata_run with trusted
root rights31 (including explicit METADATA16), dataset and uid/gid1000. Preserve
the136-byte state,72-byte result, main/borrowed engine callback, authenticated
endpoint/SPA/UTC/readiness and separate drain/export/lifetime obligations. No
new wire, main-as-client interface, allocation/thread, grant/quota/timeout change,
reset/replay or sys-init/package policy. A real error or missing cleanup/ready/
disconnect stays failure; context-entered state decides startup endpoint ownership.

Tests planned: actual main/callback with typed host FFI doubles, fixed AF07
selection/rights/data, invalid bootstrap/state/null pointers before service,
startup and all entered-service failure/cleanup modes, no duplicate endpoint
close, real exit/error/progress retention and complete C/Rust ABI offsets.
Compiling semantic omissions must fail named assertions, not missing symbols or
ABI abort. Strict Rust2021 warnings/unsafe-op/rustfmt/default Clippy; panic-abort
x86-64 static/no-redzone object, exact main/callback/imports, missing/old entry
negative linking controls. Native object is not an operational ELF or VM witness.
Commands owned60s/tests30s/quality180s with bounded child commands. Actual minimum/
current Python checks, all attempts/source/tool/env/log/cleanup identities and
compact readback before generated-output disposal. Changed inputs invalidate tests.

Applicable Foundations O/I/E, Distribution FS/SV/B applicability, approved
TD/TC/TE/CR/CP and SE-01–05; BSD-2-Clause original code and preserved Rust notices.
No release pin or shared-standard change. Technical self-review and independent
reader/owner acceptance remain distinct; independent review pending.

Simplicity: changing AF06 in place is fewer files, but silently changes its selected
owner/source contract. A separate small fixed owner preserves that consumer;
reuse its proven lifecycle with only explicit service/rights selection. A generic
multi-profile launch framework costs more than this two-profile requirement.
Remove none now because both immutable consumers must remain valid. The scoped
copy is deliberate; avoid introducing a second engine or init policy implementation.

Next external gate: Aether's fs_launch.py currently hardcodes the67-member AF06
preparation/owner/partial-link origins. The new source/object/ABI/provenance delivery
must receive a separately selected AF07 engine link/intake and native consuming
qualification. Do not bypass its guard or manufacture a stub-linked executable.
Sys-init then consumes matching executable/provisioning/readiness/shutdown.
No sibling edits/messages or additional persistence guest in this work.
UL-082/M3/R1 and shell/PID/FD/loader/packages/modes/promotion/Zsh/TTY remain open.


## Actual results and technical assessment

FMO-01–08 (summary.json maps exact names) pass on actual Python3.10.21/3.14.7;
nine compiling semantic omissions fail assertion-based host tests as intended.
All13 missing cleanup bits/unknown-bit, pre-acquisition binding validation,
post-entry error/progress/close/ready/disconnect, empty-request and contradictory
ownership cases are covered. Five original AF06 owner cases pass from unchanged
source. The typed metadata double rejects omitted METADATA16 without unwinding
across FFI. No production no-op or fixture expected-error conversion is added.
The sole inherited lint suppression mirrors the nine-argument test FFI and now
has an explicit reason. No extra runtime dependency or allocation is introduced.

Rustfmt/default Clippy/warnings/unsafe-op diagnostics and native panic-abort/
static/no-redzone/codegen-units1 builds pass. C/Rust launch/service extent,
alignment/offset and packed rejection pass. Exact native main/callback and three
imports are checked. A typed old-service definition leaves the required metadata
entry unresolved; the matching definition resolves it in relocatable composition.
Mixing old/new owners fails with duplicate main and callback definitions. None
of these C symbol-only doubles are executed or delivered as an engine.

The shipped Rustc object is2280 bytes, SHA256
`10e401f8f5aaf7c33ce70081abb5cec2a310598ec17811325728c4c0c2604b7b`,
identical on both final interpreters. Clippy emits different code; that result is
retained separately and not shipped or claimed equivalent. The first preparation
failed an unjustified cross-compiler byte-equality assertion; both compilation
results and original commands remain. The corrected plan distinguishes source
lint/build coverage from selected artifact identity. No native failure or retry.
This is object size, not RX/image/page/stack/peak-memory or operational fit proof.

Implementing Codex self-review traces one retained initialized state/SPA through
original engine entry and AF07 callback; fixed31 rights/labels/dataset and native
holders, no client-selected authority or pointer retention. Startup cleanup can
only occur before service evidence; a contradictory entered bit cannot cause
second closure. All error paths remain failures, and coherent progress is not
durability/quiescence. Full native link/origin/TLS/W^X/stack/fit and consuming
qualification remain unperformed. Independent affected-owner/reader review is
pending; no sign-off or full12-oracle independent replay is claimed.

875 current frozen producer inputs match the approved successful provider receipt.
That receipt's earlier timeout is unexplained and its batch approval consumed.
Final minimum/current syntax, quality/all released pins/adopted snapshots and
whitespace pass. Existing AF06 source/executable and77-member service remain
verified unchanged. New18-member owner input seal:
`a5113edeb55d6ae38905bca047cbf6c290dc0ff25ab958556840194586a5b052`.
Current Aether fs_launch.py remains hardcoded to AF06 preparation/source/origins;
exact new link/intake/native and sys-init requirements are in the owner proposal.
No stub-linked executable, new guest, reset/replay, scope/limit/idle allowance,
sibling edit/message, release-pin or old-seal change. UL-082/M3/R1 remain open.

Retention:506 compact source/command/output/result records were verified before disposing five exact newly owned roots.227 generated binaries/objects total54205552 logical bytes removed; net/physical disk saving not measured. Final source/record/new18-member candidate/77-member dependency/old AF06 source and30-member executable readback passes. Native builder still selects AF06; no automatic monitor or guest was started.
