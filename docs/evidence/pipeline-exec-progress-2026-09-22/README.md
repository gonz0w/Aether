# Resumable exec request handshake

Work began2026-09-22; final qualification completed2026-09-23. The private capacity
owner now retains request/reply phase,32-byte frame and offset. Each poll performs
at most one synchronous channel transfer and returns on partial progress or EAGAIN.
Both requests must match opcode84, image, authenticated slot, generation and zero
padding before any reply. Denial precedes retry; a complete successful reply
precedes snapshot intake. Polling completed state does no more channel work.

The focused host witness uses this same module with mock transport. It checks
fragment lengths1–16, repeated stalls, one operation per poll, final idempotence,
and malformed fields/padding in both requests with exact2746 rejection before
reply. This is not arbitrary native adversarial scheduling coverage. Existing
native denial, snapshot, publication, cancellation and lifecycle controls remain.

The surrounding driver still completes one child's handshake and later exec phases
sequentially. Snapshot/freeze, admission/commit/publication, grants and readiness
have not become resumable. There is no exec/I/O overlap claim or new public ABI.

## Results and attempts

Final native attempt2 passes all54 cases. `zig build test` passes, including105
Python tests and the embedded Rust handshake tests. Runtime identity covers280
inputs. Largest owner15880 bytes fits the unchanged16384-byte limit.41/81 previous
ELF/raw images are identical; all40 changed owners are requalified and every client
is unchanged. Kernel, SDK, shared pipe core, siblings, compiler flags and release
pins remain unchanged. Original code remains BSD-2-Clause.

Nine failed link-only probes and two successful probes are retained with source
snapshots. Probes1–4 tried the full replacement state machine and exceeded four
pages; that implementation was not adopted. Probes5–9 narrowed the scope but also
exceeded the limit. The final implementation shares the one-transfer primitive,
reuses validated descriptor counts and compiles the existing control-trap wrapper
out of line for exec-request profiles. No authority or cleanup check was removed.

Native attempt1 passed54 case oracles but failed the final source-integrity check
because Finder changed user/.DS_Store. It remains incomplete and unqualified.
The final harness excludes only .DS_Store in addition to its existing __pycache__
exclusion, then reruns qualification against frozen actual sources. Host results
from both attempts are retained. Build failures are not native rejection evidence.

## Reproduction and limits

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
- `python3 -m unittest discover -s tests -p test_pipe_owner.py`
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`

Preimplementation review and scope adjustment are recorded in NATIVE-SHELL-STARTUP.
The source inventory, commands, artifacts, all failed attempts and test logs are
retained here. finalize.py verifies archived bytes before deleting only the two
owned suite-output directories. SHA256SUMS seals all packet members except itself.

Next review the owner code budget and remaining dispatch state before full retained
replacement progression. Then require copied-builtin I/O while a peer's exec reply
is held, followed by completion, wait and reclaim. Interrupted/lost-reply recovery,
actual dash main/eval, unchanged consumer pipeline scripts, console/TTY, matching
full runner/connections suites and independent consumer acceptance remain open.
Persistence/OpenZFS, packages and sys-init assembly remain R1 work. This is neither
full-shell acceptance nor a whole-system security assessment.
