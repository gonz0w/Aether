# UL-007 serial SESSION preparation — 2026-09-29

The [serial handoff](../../../experiments/dash-native/SESSION-SERIAL.md) is pinned
and ready for Aether owner review/implementation. Native serial execution is
**NOT RUN**. No sibling source or existing runtime behavior was changed.

Three LF-terminated inputs preserve every accepted SESSION command in order.
A transformation assertion ties them to the unchanged original script. Phase1
checks argv and a pipeline; phase2 captures substitution and runs another pipeline;
phase3 rechecks x across a prompt, checks FD closure and stable PID, writes stderr
and stdout, and exits0. The expected program streams remain65/19 bytes. Three
`$ ` prompts yield an exact90-byte combined UART stream per parent, without echo.
Each input must wait for its own actual prompt; stdin preloading cannot qualify it.

Original dash syntax and ShellCheck pass. Eight explicitly relocated host stdin
references pass: normal0, wrong WITNESS31, corrupted pipeline bytes0 with stream
rejection, bad substitution33, fd leak35, cross-phase state loss33, PID guard36,
and stderr misrouting0 with separate-stream rejection. Exact bytes and complete
owned process cleanup were required. These are noninteractive host shell checks,
not prompt timing, native UART, identity authority, disconnect or cancellation.

The native proposal requires27 copies,21 helper replacements,24 admissions and30
terminal/reclaims across three parents, with exact identities reconciled before
replay. It preserves existing lifetime/resource limits and demands a fresh linked
owner review. It covers prompt/lifecycle ordering, owner-only UART access, short
transfers, empty-read EAGAIN, stale grants and explicit idle-parent cancellation.
Empty UART never means synthetic EOF; physical hangup/job control remain outside
this bounded request. Owner result codes and cleanup for controls must be frozen
in the producer delivery, not inferred from shell text.

Sources/helper, plans, expected bytes, Python/tool binaries, host linker and SDK
metadata were pinned before execution and checked afterward. Clang21.1.8 compiles
the unchanged host helper with C17, O2 and strict warnings; host runs use absolute
/bin/dash with explicit environment and private build roots.30-second deadlines,
16MiB stream limits and unchanged owned process runner apply. See inputs.json,
results.json and retained process receipts for exact identities and commands.

Both preparation attempts passed eight references. The initial attempt is retained
under initial-reference/: a subsequent prose clarification moved the description
of the final x check to phase3, matching the already unchanged commands. The new
handoff was repinned and host checks rerun. No failed native attempt or native
acceptance exists. See attempts.md; no prior sealed evidence was modified.

Next Aether delivers the combined interactive owner/adapter and regression packet;
userland then independently replays SERIAL-SESSION-01–06. SI-07's complete transport
and rebuilt runner/bytecount, shared SDK, independent reviews and full M3/R1 stay
open. Host build roots contain small retained references/helper binaries; no large
native build or compiler cache was produced by this preparation.

Final quality, syntax, whitespace, current input/tool preservation and three prior
sealed packets pass. See final-checks.json. Reader/owner review remains pending.
