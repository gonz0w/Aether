# Partial pipe request and child fault

Requirement: qualify abnormal child teardown without losing already committed
pipe bytes or executing a truncated request. The real copied child writes 256
bytes, sends 17 bytes of a canonical next16-byte write request, then executes UD2.
Its parent holds the reader, closes its writer, and waits at the existing private
scheduling witness until the owner observes the fault. The parent drains exactly
256 bytes to EOF before waitpid reports SIGILL (no core-dump claim), then exits0.
Two real parent/backend/child lifetimes must still produce six reclaims.

Before effects: owner validates the exact child handle's terminal kind2/detail134,
drains its now-terminal request channel through EOF into the existing 32-byte
frame, and requires precisely the expected17-byte prefix. Only then discard that
frame and release child endpoint/stdio holders. Preserve buffered bytes while the
parent reader lives. Retain the actual terminal status for wait and reclaim only
after parent collection acknowledgment and detached routes. Keep normal exit-only
expectations for old profiles. No runtime sources change during qualification.

Forbidden: treating a partial frame as a write, fabricating success/normal exit,
releasing holders on unobserved fault, truncating buffered data, requiring wait
before EOF, silently forgetting a pending reference, or accepting timeout as a
negative result. Controls: retain the discarded frame (owner 2166, zero reclaims);
map the fault as normal exit134 (parent 90 then owner 2163, zero reclaims). Existing
retained writer/early EOF controls remain in the complete connections suite.

Scope: private Aether native probe/dispatcher and harness. O-02–05, I-01/03–06,
E-01–08 and the local simplicity/testing process apply. No kernel, ABI, SDK,
sibling, release pin, service, allocation or quota changes. Reuse the existing
native wait-status mapping. Raw transport borrows owned stack arrays; the UD2 is
an intentional user-space fault, never a kernel fault. New C uses pinned
clang-format21.1.8, Rust1.98.0 edition2024/skip_children; preserve old source style.

Simplicity: extend the existing per-client frame/terminal loop, rather than adding
cancellation or recovery protocols. A single named fault schedule is sufficient
for this requirement; do not imply all fault races or complete recovery. No old
mechanism can be removed yet. Selected tests: focused positive and two semantic
controls, full connections plus launch/console regressions, host/harness/format,
workflow and immutable pin checks. Preserve each attempt and frozen sources.
Document evidence and remaining gaps in STATE, native reference and workflow.
Forced stop of a fully queued write, silent stalls, copy rollback, SIGPIPE,
same-client pipe reuse, actual dash and R1 assembly remain separate work.
