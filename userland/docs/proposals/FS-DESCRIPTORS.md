# Read-only file-description core — UL-007/081/082

Current maintained source now extracts shared state into `file-descriptions.rs`;
`descriptors.rs` is the dedicated Owner adapter and the [AF07 adapter](FS-REMOTE-DESCRIPTORS.md)
uses that same core over a fresh service connection. Failure::Policy becomes
Failure::Source in the maintained source-only API. The original candidate/evidence
below stays immutable and describes its original scope. Twelve local tests and
eight omissions rerun after extraction; remote evidence is separate.

Implemented private Rust core: `experiments/filesystem-service/descriptors.rs`.
It owns one **dedicated** existing Owner policy context and one trusted peer
attachment. It is not a wrapper to take over a running multi-client AF07 server.
There is no new service wire/opcode, libc/C entry, native image or supervisor
integration. It is the local shared-offset/lifetime implementation for the next
filesystem-backed descriptor translation step.

Root authority is explicit LOOKUP|READ; successful file lookups attenuate to READ.
Peer identity must come from authenticated provisioning; numeric FD/PID/UID/path
labels grant no native authority. Owner still enforces attachment, epoch, handle,
rights and backend lifetime. Original AF07 service/client seals are unchanged.

| Local operation | Behavior and bounds |
| --- | --- |
| open_read | One policy-validated component1–255 bytes; existing regular files only; independent handle and offset0. Reject a directory after closing its lookup handle. |
| duplicate | Lowest free file FD at/above minimum; same retained description/offset; caller explicitly chooses new descriptor's close-on-exec bit. |
| read | At most4096 bytes; advance shared offset only after successful actual Owner read; zero unused/error bytes. |
| seek | Set/current/end with checked signed64 results; end uses Owner's coherent Entry size. Failed seeks preserve offset. |
| close | Remove one descriptor; close the retained Owner handle only after its last alias. FD numbers can be reused; Owner handle serials are not reset/reused. |
| commit_exec_close | Close flagged descriptors after confirmed image admission; preserve unflagged aliases and their shared offset. |
| disconnect/Drop | Local policy detach and sole backend context release. Not native endpoint, SPA/export, quiescence, halt or reclaim evidence. |

FD0–2 are reserved for console translation outside this core. File FDs3–15 give
13 fixed bindings/descriptions; root plus13 handles fits the existing16-handle
policy table. Alias scans avoid another reference counter. Capacity is checked
before backend lookup. This allocation-free core takes exclusive `&mut self`
for effects; no cross-process FD/fork sharing or concurrency protocol is invented.

Returned Failure values preserve original policy errors rather than replacing
unsupported behavior with success. Known positive backend errno errors clear
data and preserve offsets. Invalid metadata/counts, retired/stale/closed context,
uncertain completion or failed final close retire local admission, revoke local
references and shut down the sole context. Future operations fail closed. There
is no reset/replay or inferred native recovery.
The existing Owner requires the full coherent count up to EOF for each provider
read. This core inherits that rule: a shorter-than-expected provider count is an
invalid completion, not an implementation of general interrupted short reads.

The experimental signed offset/request range is stricter than full POSIX: a
read whose requested end exceeds signed64 is rejected before provider effects,
even if it might meet EOF. No full POSIX conformance claim follows. No writes,
create/append, path traversal, modes/credentials/stat translation, TTY, fork,
image loader or executable admission is implemented. Read-only rights do not
substitute for those requirements.

Exec remains an external commit boundary. The dispatcher must preserve FD state
through failed lookup/read/image preparation, settle actual native admission,
then commit close-on-exec. Ambiguous exec cannot safely call commit or restore
state by replay. This core supplies the local destructive step only; its tests
are not failed-exec or native rollback witnesses.

[Evidence](../evidence/filesystem-descriptors-2026-10-21/README.md) uses actual
pinned AF07 Owner with synthetic storage, not an AF07 wire/native engine. Next
integrate authenticated process/FD dispatch and AF07 client transport without
duplicating live Owners or violating the SPA borrow; qualify real reads,
copy/exec/FD errors, final disconnect/export/reclaim and fresh boot separately.
Immutable executable loading, packages, Zsh/TTY and M3/R1 remain open.
