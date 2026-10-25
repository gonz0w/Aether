# In-place FILE broker / mapped owner qualification

Scope: UL-007/081/082, sys-init BG-073 and BG-070. Implementation-agent review;
independent review and native acceptance remain pending. No guest ran, no old
sealed delivery/release pin changed, and all code/stack/data/VM limits stay fixed.

The pre-code requirement, lifetime/authority/unsafe/simplicity review and exact
commands are in [FS-BROKER-INIT](../../../userland/docs/proposals/FS-BROKER-INIT.md).
Final elementwise source hashes match the retained passing producer/component
checks. The owner qualification builds from those same libraries and current
sources; its final report explicitly rejects code fit rather than returning success.

| Selection | Result |
| --- | --- |
| New fs_in_place broker | 35 actual process/remote tests, 15 compiling semantic controls, safe-borrow denial, strict rustfmt/Clippy and host/no_std builds pass |
| Existing client | 12 tests/eight compiling controls pass; current source/checker hashes match |
| Existing by-value process | 31 tests/13 controls pass; default-source-impact.json proves the only final source differences from that receipt are inside disabled fs_in_place functions |
| Consuming mapped owner | 24 existing gate/stream/capture/region tests plus two new in-place/failure/drop/workspace tests pass; host/native libraries and strict Clippy pass |
| Concrete Native framed subset | size-z .text16544; size-s17360; current limit16384. Code-fit blocked, not native admitted |
| Constructor stack observations | minimum_boot reserves192 bytes and pushes24 (216-byte prologue); largest observed fixed reservation520. This is not complete peak-stack analysis |
| Rejected typed-array comparison | Same host tests pass; .text16720 and1104-byte local reservation, so smaller elementwise implementation retained |
| Checker CLI | Help/version0, missing/unknown usage64, no ANSI or preparation; actual code-fit block emits JSON and exits2 |

The Native specimen preserves the prior independent roots for RPC, gated capture,
copy/local publication, exact-ready/parent, settlement, disconnect and boot, changing
only broker construction. It is not a kernel entry or a runnable complete owner;
callbacks have no caller and are never executed. It is not a successful stub.
These measurements do not prove every unified owner arrangement must be this size.
Full actual native transaction/entry/readiness/shutdown and complete code/peak-stack
fit remain BG-070 work before any new guest or persistent Zsh qualification.

Attempts retained, including failures:

1. Initial candidate stops at Clippy's drop_non_drop in a test. Scope the uninitialized
   slot naturally instead of suppressing the lint. No runtime failure occurred.
2. The occupied-generation control fails the intended test via unwrap, which the
   checker correctly refuses as an assertion oracle. Add explicit initial record
   assertions; all15 controls then fail their named semantic assertions.
3. The first consumer build stops on missing explicit client/service dependencies
   for fd-protocol. Supply its real dependencies; no unresolved-symbol relaxation.
4. LLVM inspection initially receives Rust's DYLD_LIBRARY_PATH and cannot load its
   own LLVM dylib. Limit that variable to Rust tools; compiler/test successes are
   still attributed to their original run, not a native witness.
5. Required size-z subset16544, size-s17360. First-shutdown-only binding clearing
   preserves16544 (no measured size gain). Typed-array initialization gives16720;
   restore the smaller qualified elementwise source exactly. Neither raises limits.
6. Final checker fails closed at code fit after26 host tests. CLI-only revisions
   requalify the checker; no storage guest is retried or persistence failure hidden.

Records retain exact source/tool/library identities, commands/outcomes and short
failure logs. Owned binaries/rlibs/source work roots are removed after recording
hashes; there are no new build/test archives, copied SDKs or image bundles.
The size-s alternative changes only the top-level optimization of the same roots.
No fresh storage/media, owner sign-off, full UL/M3/R1, shell or ISO claim follows.

The first workflow inventory check rejects component paths added to its strict
root-only native-reference/tool sets. Register the cross-component test group
there and the script in sys-init’s existing quality surface instead; retain
root coverage equality and all checker rejection behavior.

Changed-document link verification also found two pre-consolidation lowercase
`aether/` references in userland’s architecture and eight uppercase sibling routes
in the touched filesystem README. Point those links to the kernel root; no
runtime/source-pin change.

Cleanup removed 299439249 logical bytes across 16 owned
generated roots. Physical disk reclamation was not measured. Byte-identical result
records have one retained copy with explicit SHA256 aliases in record-aliases.json.

Final documentation/process checks: root workflow175 groups and Experience pin;
userland quality/offline pins; sys-init quality/Foundations pin;1535 changed-document
file destinations all pass. No broad kernel or native suite was selected for this
leaf Rust construction integration. Resource-fit failure remains visible.
A retention-note append initially used the component cwd and found no root receipt;
no source/evidence was changed before the corrected root invocation.

Receipts retain complete JSON objects and exact argv, serialized compactly; use
JSON tooling for expanded inspection. capture-normalization.json binds original
and retained bytes; upstream/cleanup receipt hashes still describe their original
captures. Human excerpts trim trailing whitespace for the commit gate. No prior
frozen evidence was edited. The first commit attempt rejected excerpt whitespace.
A provisional deduplicating compactor then encountered the CLI’s different row
shape; two provisional receipts were restored byte-for-byte from the pending Git
index. The compactor was discarded in favor of lossless JSON serialization.
