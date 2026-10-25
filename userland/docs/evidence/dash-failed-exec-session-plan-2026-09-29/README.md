# Failed-exec session handoff preparation — 2026-09-29

UL-007. **Ready consumer workload; native execution NOT RUN.**
[Contract](../../../experiments/dash-native/SESSION-FAILED-EXEC.md) and its manifest
pin a new composed script, exact60-byte stdout and25-byte stderr, and the unchanged
helper. It tests missing127 and denied126, then a healthy argv command/pipeline,
closed descriptors, unchanged parent PID and final parent stderr. Native repetition
requires three complete parents with owner-verified error/cleanup facts.

Original script passes `/bin/dash -n` and ShellCheck with the declared dash dialect.
The successful attempt runs seven host references with only explicit /inputs/
relocation under a private build root, plus named semantic mutations. Clang21.1.8
builds the unchanged helper using the recorded host SDK and absolute linker. All
commands have30-second bounds,16MiB streams and complete owned process cleanup.
No original target paths are executed, installed or created on the host.

| Host reference | Actual result |
| --- | --- |
| Positive | exit0, exact60-byte stdout and25-byte stderr |
| Missing path made non-executable | exit51, no output |
| Non-executable object removed | exit52, no output |
| Second command skipped | exit52, no output |
| Wrong WITNESS | parent53, only exec-errors prefix |
| fd3 deliberately leaked to final helper | parent55, only exec/argv/pipeline prefix |
| Healthy pipeline byte changed | exit0 but ordinary exact-output oracle rejects |

The first attempt failed before reference execution: PATH=/nonexistent, intended
for the shell workload, also prevented Clang from finding its host linker. Raw
failure, commands, inputs and private build directory are retained at packet root.
Attempt2 uses a pinned absolute linker and a separate clean compilation environment;
its script/helper/expected bytes are identical to the first attempt. All seven
references then passed. Results/receipts and derived source bytes are in attempt-2/.
This is host shell/process preparation, not native authority, retirement, resource
or sanitizer coverage. Python minimum-version execution was not newly qualified.

Current native integration gap: session-client locally rejects every non-helper
path with EACCES. Owner-backed missing lookup and non-executable denial are required;
a local pathname special case is insufficient. Proposed logical work is21 copies,
12 successful replacements,15 admissions and24 terminal/reclaims across three
parents. Existing slot reuse appears to reach the fifteen-lifetime ceiling exactly;
owner phase/slot/channel reconciliation and linked code/stack review are required.
No lifetime or observation limit is widened. Both failed children close only their
own stderr; later parent stderr must still work. Failed-command human diagnostic
coverage is explicitly excluded; there is no output truncation or renderer change.

Negative native request/authority, stale/retained-child, parent-stderr and cleanup
oracles must be frozen by the owner before replay. Host status tests do not replace
them. EXEC-SESSION-01–06 remain NOT RUN. Failed-exec component and RECOVERY acceptance
remain unchanged; shared SDK, SI-07, reader review and full M3/R1 remain open.
Final local gates and preservation checks are recorded in final-checks.json.
