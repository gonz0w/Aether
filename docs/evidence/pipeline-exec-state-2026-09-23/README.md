# Retained exec replacement progression — 2026-09-23

The private capacity owner now advances replacement through retained phases:
request or legacy token, descriptor snapshot, observed freeze, native admission,
descriptor commit/publication, filtered table, standard-stream grants, authenticated
report and native readiness. The state binds the owner-supplied child handle, slot,
generation and channels at construction. It owns all partial buffers and offsets.

Each poll performs at most one channel transfer or one bounded existing transaction
and returns on partial progress/backpressure. Request handling reuses the qualified
ExecRequest module; descriptor/admission/commit checks remain in their existing
helpers. Report intake is deliberately limited to three bytes per poll, qualifying
retention across a fragmented16-byte identity/role report. Completion and cancelled
states perform no further polling work. No pointer survives a synchronous trap.

The admitted-but-unpublished cancellation boundary remains between Admit and Commit.
The partial-table cancellation still occurs after publication and exactly seven
sent bytes. The driver performs the existing confirmed-stop/holder cleanup before
returning and discards its retained transfer state. No cancellation waits occur
inside poll. The driver still completes one child at a time: this is not yet exec/
I/O interleaving, independent consumer acceptance or a full shell.

## Bounds and compatibility

Exec variants explicitly use005 and user/native-capacity/linker.ld with the qualified
24576-byte limit. Non-exec fixtures retain004 and their four-page linker. An added
basic exec witness runs the same new state machine under004 within16384 bytes.
The existing kernel mappings, ABI19, grants, worker/channel counts and backing pools
are unchanged. The driver retains one state on its existing stack; review combined
stack use before retaining several states alongside the I/O dispatcher.

The shared driver has one100000-poll ceiling per child, stricter than resetting a
budget for each former blocking loop. It retains timeout diagnostics2746 for
request,2730 for snapshot,2733 for freeze and2734 for remaining transfer/readiness.
Malformed, stale-authority, denial and cancellation oracles remain unchanged.
No kernel, SDK, shared pipe core, client, sibling or standards-pin change is made.

## Attempts and reproduction

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`

Native attempt1 passed66 cases. Final review restored the phase-specific timeout
diagnostics before a second complete qualification; both source sets and host logs
are retained. No failed native cases prompted that adjustment. The suite includes
all previous65 cases plus basic exec under the legacy envelope. Existing controls
cover denied images, CLOEXEC rejection, stale publication and both cancellation
boundaries; fragmented reports are exercised throughout exec profiles.

The preimplementation review and diagnostic follow-up are in NATIVE-SHELL-STARTUP.
finalize.py verifies frozen sources, archives and actual artifact bytes before
removing only the two owned suite-output directories, excluding Finder metadata.
SHA256SUMS seals the packet. Older evidence remains immutable.

Next integrate per-child progression with the I/O dispatcher, preserving request/
report versus I/O framing. Require a copied builtin to progress while a peer's exec
reply is deliberately held, then finish replacement, wait and reclaim. Multi-child
stack usage, interrupted/lost-reply recovery, actual dash main/eval, unchanged
consumer scripts, matching full suites and independent acceptance remain open.
Persistence/OpenZFS, packages and sys-init assembly remain separate R1 work.

Final native attempt2 passes all66 cases in184.092 recorded case seconds on281 frozen runtime inputs. Host suite passes105 Python tests plus Zig/Rust checks. Largest owner17016 bytes fits24 KiB; basic exec13072 passes the old envelope.43/81 previous ELF/raw images are identical; all38 changed exec owners requalified and all clients unchanged. Kernel mapping span remains8007680 bytes. Both native attempts passed; no failed native cases occurred.
