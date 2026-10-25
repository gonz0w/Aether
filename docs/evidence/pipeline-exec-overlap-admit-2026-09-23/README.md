# Cancellation before publication with active I/O — 2026-09-23

The private overlap fixture now tests cancellation at both sides of publication.
The new variant stops slot4 at the retained Commit phase, immediately after actual
image admission and before descriptor commit or native publication. Admission
already verifies receipt(sequence1,image0xc002,frozen1), readiness0 and freeze1.
The dispatcher holds this phase instead of polling Commit. The child cannot consume
replacement grants or send replacement I/O before cancellation.

The shared cleanup path observes exact143/kind3/readiness0 from the bound native
handle. It then verifies publication of the stopped instance rejects EBUSY(-16),
clears retained frame/table/request state, and releases the existing pipe and
standard-stream holdings. Pre-commit holdings are removed directly; no successful
descriptor commit or replacement readiness is fabricated. All backing is reclaimed
only through the existing later terminal/reclaim sequence.

The copied writer and relay finish. The relay drains ten first-pipe bytes to EOF
and receives EPIPE for each second-pipe write after reader removal. Parent public
musl wait calls collect each child once, preserving the reader's SIGTERM15 outcome
rather than treating detail143 as a normal exit. Three generations require12
admissions and15 reclaims. The existing first-writer/partial-denial overlap witness
and both standard-stream and pipe ledgers remain active.

## Controls and scope

The three new cases reuse the existing stop clients and cleanup path:

- Positive: admitted-but-unpublished stop, rejected late publication and complete
  surviving I/O/waits/reclaim.
- Omitted stop: child remains live, state remains retained, exact2770 after32 held
  cancellation polls with zero reclaims.
- Retained state: observed terminal cannot complete cleanup without clearing;
  exact2772 before holder release or reclaim.

Timeout or generic panic is not acceptance. Existing post-publication cancellation
and its two controls remain in the full suite. This is bounded injected stop
coverage, not arbitrary peer-fault/lost-reply recovery, signal delivery, interrupted
parent reply handling or independent full-dash acceptance.

## Resources and compatibility

The new positive ELF's extracted text matches its tested raw owner exactly. The
reviewed start/poll/commit/descriptor-prepare/memory-leaf chain remains3952 bytes
within4088 usable, leaving136 bytes. Cancellation observation is shallower. This is
a scoped linked-binary review, not a general compiler-independent stack proof.
Future caller/buffer/compiler/participant changes require renewed stack review.
The one-page stack and existing24-KiB code/participant/channel/backing limits remain.
New positive/omission owners are18136/18040/17640 bytes.

85/88 prior ELF/raw images are identical. The three prior overlap-stop owners
changed with the shared boundary predicate and are requalified; all clients are
unchanged. Runtime changes are confined to copies.rs, its dispatcher call site and
the capacity harness. Kernel, shared pipe core, SDK, clients, siblings, dependencies
and released pins are unchanged. The freeze covers281 runtime inputs.

## Reproduction and retention

```sh
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

NATIVE-SHELL-STARTUP records the preimplementation requirement, forbidden outcomes,
authority/resource review and simpler shared cleanup choice. finalize.py verifies
source snapshots and all generated archive/live bytes before removing only the
verified duplicate suite output. SHA256SUMS seals this packet; older evidence is
immutable. Final native and host results are recorded below once complete.

Next is interrupted parent wait reply ownership before broader shell integration.
Actual dash main/eval, unchanged consumer workloads, matching full suites and
independent acceptance remain open. Persistence/OpenZFS, packages and sys-init
assembly remain R1 requirements; this is not a full-shell handoff or release gate.

Native attempt1 passes all74 cases in207.783 recorded case seconds. Host checks pass105 Python tests plus Zig/Rust checks. New positive and exact2770/2772 omission controls pass.85/88 prior images are unchanged; all three changed stop owners requalified. One native attempt, no failed native or harness cases in this slice.
