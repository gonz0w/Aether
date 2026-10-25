# Native exec image gate — 2026-09-10

The opt-in native connections experiment replaces a frozen worker with a distinct
boot-selected ELF under the same PID, parent and lifecycle identity. Commit retains
sequence/image identity and holds the replacement until matching publication.
This is an image-only producer witness: no Unix descriptor table, CLOEXEC policy,
public execve entry point or independent SDK/dash acceptance is supplied here.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#native-exec-image-gate-selection--2026-09-10)
records authority, failure ordering, resources, unsafe boundaries and simplicity.
The [native contract](../../NATIVE-C.md#native-exec-image-gate--2026-09-10) defines
the three supervisor-only operations and their errors. The kernel reconstructs
fixed backing under IF=0 on the supervisor's CR3, using immutable images admitted
at boot. Complete argument validation precedes mutation; there is no recoverable
loader failure after destruction starts. No sibling, installed SDK, dependency or
released standards pin changes are part of this work.

## Executable evidence

Final frozen sources pass 168 connections cases, 431 command-runner cases, five
launch cases and seven two-core regressions: 611 target cases in total. Host checks
pass, including the 39 execution/signal tests and 98 Python harness tests. Commands,
UTC start/end, elapsed time, exit codes, case oracles and raw outputs are retained
in the mode logs, timing JSON and results JSON. `qualification.json` records exact
235 source files, 12,067 target artifact files and the largest bounded Rust owner
(6,648 bytes within its 8,192-byte limit); all selected suites
finish within their 1800-second review budgets.

The positive exec case rejects bad authority, image, token, pointer and argument
records without replacing the old program. Cancellation lets that original program
verify its old TLS/stack cookies and freeze again. A successful commit selects a
distinct C ELF; retained query reports the new identity while cancellation, duplicate
commit, unpublished copy and stale publication are rejected. After 32 yields,
matching publication runs the replacement's PID/parent, argv/environment, fresh TLS,
bootstrap grant and denied worker-authority checks. Its terminal result is61.
The witness repeats one replacement in each of two process generations, with peer
launches ending29 and six total reclaims. It does not prove repeated exec within
one process lifetime.

| Deliberately broken control | Required observation |
| --- | --- |
| `exec-early` releases the worker at commit | Owner2031, zero reclaims |
| `exec-token` accepts stale publication | Owner2032, zero reclaims |
| `exec-copy` permits copying an unpublished image | Owner2035, zero reclaims |

The copy probe supplies valid fresh channel endpoints and a free destination slot.
Allocation/cleanup failures use2036, so an unrelated resource failure cannot pass
that control. All four exec serial logs are retained separately. A generic panic,
watchdog or nonzero exit is not a passing negative control.

## Preserved attempts and review correction

- `attempt1/`: fixture failure before exec admission. The owner copied the13-byte
  environment string into a12-byte slice, producing owner999. The bound was corrected
  to13; the incomplete target attempt, passing host/launch runs and inputs remain.
- `regression-attempt1/`: infrastructure failure before boot. The sandbox refused
  the QMP Unix socket. The same selected regression was retried with permission for
  its local socket and passed. This is not evidence of a kernel failure.
- `attempt2/`: superseded qualification. The167-case connections suite, host,
  five launch cases and seven core regressions passed. Review found that process-copy
  could unpark a committed unpublished replacement. The command suite was intentionally
  interrupted, its partial results retained, and all source edits waited until that
  run stopped. The copy guard and2035 control were added before final qualification.

The three target attempts retain source/artifact archives and logs.
`collector-attempt1.py` and `collector-attempt1.log` retain a separate evidence
bookkeeping failure: the broader regression inventory adds six existing license,
boot and toolchain inputs not listed in the previous native-only snapshot. The
collector now classifies those separately from the two new fixture sources.
No runtime or test input changed for that correction. The evidence collector
reads back their archive members; no failed attempt is replaced by a passing receipt.

## Identity and limits

`sources.json` and `sources.tar.gz` bind the final source snapshot. `runtime.patch`
records the five changed existing implementation files and two new fixture files
against the sealed exec-preparation baseline. `target-artifacts.json` and
`target-artifacts.tar.gz` retain every file in the four final target directories.
`compatibility.json` compares the164 older connections payloads outside boot entropy
bytes32..79; those payloads match. Kernel binaries are rebuilt and can differ:
passing regressions qualify them, not an assertion of kernel binary identity.

`final-checks.json` retains the post-documentation host, scoped Zig/Rust/C format,
standards, experience, workflow and whitespace checks. The preceding evidence
manifest and the simplicity snapshot's pinned digest/four files are verified.
`manifest.json` seals every file in this packet except itself.

Existing bootstrap entropy is reused: this makes no fresh-entropy or ASLR claim.
Signal-transition constructors have host coverage; live native signal transitions,
stale anonymous mappings and a zero/reuse negative control remain follow-up work.
The fixture retains endpoint grants but does not implement an exec-time descriptor
table, shared file offsets or CLOEXEC cleanup. Backend reply-loss composition,
unknown commit outcomes and resource-accounting integration are also pending.
Next compose the connection owner's descriptor preparation/publication with this
kernel gate before native execve and actual dash acceptance. R1 remains unfinished.
