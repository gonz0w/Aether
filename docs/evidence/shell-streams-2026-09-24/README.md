# Serial streams without script-specific captures

2026-09-24. Final qualification passes all 105 capacity cases and 110 Python tests
plus Zig/Rust host checks. This is scoped serial-forwarding evidence, not SESSION
or full-shell acceptance.

## Change and scope

AENMX006 serial stdio now forwards validated requests without cumulative stdout/stderr
captures, input counters or expected script bytes. It retains caller, generation,
holder, frame/padding and direction checks, synchronous pointer lifetime, EAGAIN,
short transfers and explicit closure. Completion checks holder lifetime. The existing
finite driver/request limits, 16-byte RPC framing and one-byte UART calls remain.
There is no new queue, allocation, ABI, kernel change, public service or resource cap.
Nonserial fixtures retain their capture semantics and compatibility controls.

The host now owns the complete output oracle. Real dash executes a long stdout/stderr
builtin command, a three-stage parent-created pipeline and a long follow-up command
before exit. Both streams exceed the old 32-byte capture. Across three generations:
9 commands/prompts, an expected 178 stdout bytes and 75 stderr/prompt bytes per generation,
15 successful terminal records and 15 reclaims. The owner finally closes UART authority.
Parent/copies still verify that direct UART access is denied. The host verifies the
combined UART byte stream; this does not independently capture two separate streams
or satisfy the composed-session stdout/stderr acceptance requirement.

A deliberate native stdout corruption changes `p` to `P`. Guest execution must still
complete and reclaim everything, but the ordinary host validator must raise exactly
`pipeline UART output mismatch`. The suite accepts this control only for that named
host failure. Wrong grant still rejects owner2795 before a prompt; capacity-disabled
006 still rejects before admission. A crash, timeout, missing cleanup or skipped
command cannot satisfy the corrupted-output control. Native/emergency markers and
upstream ASCII prompts retain their bytes.

Only serial forwarding is script-independent here. The pipe/copy/wait driver still
has fixed job topology and byte-count expectations. This is not arbitrary repeated
jobs, full dash, a published SDK, TTY acceptance or R1 assembly.

## Consumer intake and next work

`consumer-inputs.json` and its readback-verified archive pin userland's current
`experiments/dash-native/SESSION.md`, manifest, unchanged composed.sh, expected streams
and helper source. SESSION-01–06 requires external argv, two pipelines, substitution,
final fd closure and one parent identity throughout, repeated with complete cleanup.
That workload has NOT RUN here. Its earlier twelve-script acceptance is unchanged.

Next define/freeze the owner's lifecycle accounting and rejection oracles, then run
that entire unchanged composed script through one dash main. Do not substitute this
serial test or separately booted scripts for SESSION acceptance. Shared runtime/SDK,
independent review, broader TTY/signals, filesystem and sys-init/package integration
remain open. No sibling, released standard or prior sealed evidence was modified.

## Checks and resources

- `attempt-1`: focused native positive, first attempt passes.
- `attempt-2` and `attempt-3`: both complete 105-case native suites pass. The final
  run removes the obsolete guest-panic classification from the host corruption
  control, applying normal admission/terminal/mapping checks too. All 253 compared
  ELF/raw/kernel artifacts are identical across this harness-only correction.
- All three host runs pass 110 Python tests plus Zig/Rust and standards/workflow
  checks. The final run binds all test/runtime inputs in `host-inputs.json`; prior
  runs and their inputs are retained. Five new host tests exercise meaningful
  stream, terminal, prompt, cleanup and panic counterexamples.
- `stack-review.json`: serial owner 17960 bytes, 656 fewer than before. Reviewed
  linked critical depth 3888/4088 leaves 200 bytes, up from 88. Existing nonserial
  parent/early-reader paths remain 3968/3984. Raw owner bytes match linked ELF text.
  This is scoped inspection, not a formal whole-program stack proof.
- `legacy-comparison.json`: among 142 compared nonserial ELF/raw images, 87 are
  identical and 55 Rust owners have code-generation changes, qualified by the full
  capacity suite. All 105 kernel executables are identical to the preceding packet;
  existing connections/runner source code is unchanged.

The full matching connections/runner suites in the preceding packet are prior
qualification, not rerun results here. Current selection is the complete affected
capacity suite and host checks. A later SESSION delivery requires its own matching
producer/consumer regression and acceptance.

## Reproduction and evidence

```sh
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 -m unittest discover -s tests -p test_pipeline_console.py -v
```

Exact compiler/VM commands, tool/SDK pins, source bytes, logs, terminal outcomes and
host exchange events are retained. `run-attempt.py` records monotonic suite duration,
UTC start/end and exit code. Sources are frozen during qualification. Archive/readback
and original-file SHA verification precede deletion of owned duplicate outputs.
All attempts are preserved; there have been no failed native attempts in this step.
The existing dirty working tree is preserved, not claimed as an independent clean
release build. Previous source/manifest bytes are immutable.

Archive/seal retry: generated `.DS_Store` changed during the first final-run archive.
Readback verification rejected it before deleting originals or publishing a manifest.
Every other member matched. The failed archive, initial hash inventory, mismatch
audit and seal failure are retained; only the original metadata digest survives for
its earlier version. The retry verified all members and then removed the duplicate
directory. See `archive-triage.md`; no native source/artifact drift or test failure
was found, so no unrelated test rerun was performed.
