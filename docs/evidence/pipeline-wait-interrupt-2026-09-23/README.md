# Interrupted parent wait reply — 2026-09-23

The private overlap fixture now stops the parent after collecting its first child
result and sending seven of32 successful wait-reply bytes. Collection ownership
and reply delivery remain separate: the collected bit survives partial delivery,
stop request and terminal observation. Exact143/kind3 from the bound parent handle
is required before abandoning the retained reply. Cancellation is recorded separately
from the three delivered probe replies; no successful-result delivery is fabricated.

The cancelled wait state must retain exactly one collected child, three completed
probes, no pending reply and zeroed frame/offset. Later polls return without reading,
sending or collecting again. Final completion rechecks these invariants. Parent
channels and backing remain until the existing terminal/close/reclaim sequence.
The parent had already closed its descriptors before the wait dispatcher started;
child descriptors remain owned by those children.

The final reader's I/O is held until cancellation, and its live native state is
checked at interruption. Remaining children must then finish both pipes, exact
stdout/stdin/stderr, normal exits and all15 reclaims over three generations. The
original exec-denial/first-writer-progress witness is also required. The fixture
uses the unchanged parent and child programs; parent execution ends partway through
its first successful wait reply rather than completing the normal eight replies.

## Controls and limits

Four new opt-in cases cover the positive and:

- Missing stop: parent remains live and no reply state is cleared; exact2780 after32
  held cancellation polls, zero reclaims.
- Lost collection: after observed terminal, losing the already-collected child's
  record rejects2781 before reply cleanup/reclaim.
- Retained reply: after observed terminal, uncleared frame/offset rejects2782 before
  successful cancellation/reclaim.

Timeout, arbitrary panic and generic nonzero exit are not acceptance. This is
terminal-parent cancellation, not retry after a lost reply to a live parent,
arbitrary transport failure, orphan/reparent policy or general crash recovery.
Those semantics must be specified where the actual consumer requires them; this
fixture does not invent a new retry/session protocol or claim a full shell handoff.

## Resource and compatibility review

The positive ELF's extracted text matches its tested raw owner exactly. Reviewed
start/replacement-poll/commit/descriptor-prepare/memory-leaf depth is3936 bytes of
4088 usable stack, leaving152. Wait cancellation is shallower. This scoped linked
binary review is not a general stack proof; compiler/buffer/caller growth requires
renewed review. No stack page, participant, channel, backing budget or code ceiling
is added. Positive/mutant owner sizes are17512/17480/17432/17448 bytes within24 KiB.

78/91 previous ELF/raw images remain identical;13 wait-capable private owners change
with the shared completion predicate and are requalified. All client binaries remain
unchanged. Runtime changes are limited to pipes.rs, owner terminal expectations and
the capacity harness. No kernel, SDK, shared pipe core, sibling, dependency, unsafe
boundary, released pin or public protocol changes.281 runtime inputs are frozen.

## Reproduce and retain

```sh
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

NATIVE-SHELL-STARTUP records the preimplementation requirement, forbidden outcomes,
security, resource and simplicity review. finalize.py verifies source snapshots,
archives generated outputs and verifies every archive/live byte before removing
only the duplicate suite directory. SHA256SUMS seals this packet; older evidence
remains immutable. Results are recorded below after qualification.

Next trace the actual dash consumer path into the combined dispatcher and define
the narrow supported exec/wait failure contract before integration. Do not block
that POC on a speculative general recovery framework. Unchanged consumer workloads,
matching full suites and independent acceptance remain open. OpenZFS persistence,
packages and sys-init assembly remain separate R1 requirements.

Native attempt1 passes all78 cases in217.885 recorded case seconds. Host checks pass105 Python tests plus Zig/Rust checks. The new positive and exact2780/2781/2782 controls pass.78/91 prior images remain identical;13 changed private owners are requalified and all clients unchanged. One native attempt; no failed cases in this slice.
