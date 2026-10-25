# Extended parser checks — UL-062

Run from the repository root on the provisioned macOS host with Python 3.10+:

```sh
python3 -B experiments/command-runner/check-parser-extended.py
```

The default requires ASan and UBSan. The current host times out before the first
ASan-instrumented control completes; that is failed coverage. To run the explicitly
limited UBSan selection:

```sh
python3 -B experiments/command-runner/check-parser-extended.py --ubsan-only
```

Host static analysis, observational RSS metrics, forked parser concurrency and
a 256-round host transport loop:

```sh
python3 -B experiments/command-runner/check-extended-host.py
```

That command uses UBSan only by design. It does not retry ASan.

Pinned ASan diagnosis (deadlock inventory, not a sanitizer pass):

```sh
python3 -B experiments/command-runner/check-asan-host.py
```

Family/stage inventory and native ASan compensation limits (no native rerun):

```sh
python3 -B experiments/command-runner/check-extended-matrix.py
```

These commands accept --help and --version. Invalid usage exits 64; execution errors
exit 1; successful checks within the selected scope exit 0. Progress/errors use
stderr; final scope uses stdout. Output is plain ASCII without color or animation.
No VM, network provisioning or native SDK is needed. Clang is verified against the
existing pinned libc evidence; builds never install to a real prefix.

Every attempt retains sources, plan, command arguments/environment, tool/runtime
hashes, binaries, raw streams and owned process cleanup receipts beneath a private
build/parser-extended-* directory. Inspect summary.json and the failing label's
stderr/process.json before retrying. Keep failed attempts. Each child has a
30-second wait and 16 MiB output-file limit, followed by bounded process-group
cleanup. Reduction also enforces 225-byte inputs, 1024 oracle calls and 180 seconds
between calls. These are per-command and per-gap limits, not a total deadline or
RSS limit.

The C fixtures write `failure.bin` and `failure.json` with exclusive create in the
child's private working directory. Do not point them at a shared output directory.
Semantic assertion failures exit 90 after successful retention. Missing, empty,
oversized or invalid replay arguments, I/O errors and output collisions exit 91
and must not be reported as parser failures. `--replay FILE 0|1` is an internal
fixture contract, not a public CLI.

| ID | Family and oracle | Layer/stage |
| --- | --- | --- |
| PXE-01 | Existing valid/invalid parser controls, atomic publication | Host memory/UB; local regression |
| PXE-02 | 171360 single-byte substitutions, 675 wrong lengths, three valid seeds; canonical carrier and owned invocation properties | Host property/mutation; manual extended |
| PXE-03 | Isolated reserved-byte acceptance defect must trigger the canonical-carrier oracle, exit 90 | Host harness health; extended |
| PXE-04 | Deliberate heap overrun must report AddressSanitizer heap-buffer-overflow | Host instrumentation health; blocked on current host |
| PXE-05 | Deliberate signed overflow must report UBSan signed integer overflow | Host instrumentation health; extended |
| PXR-01 | Semantic failure retains exact bytes, length, must-accept and oracle; replay exit 90; original parser accepts the same input | Host fuzz retention; extended |
| PXR-02 | Byte deletion and nonzero-to-zero reduction keep only the same named oracle; local minimality for those operations | Host fuzz minimization; extended |
| PXR-03 | Empty, max, oversized, missing and invalid-expectation replay; exclusive output collisions stay 91 | Host harness health; extended |
| PXR-04 | Synthetic deletion, zero reduction, non-reproducing input and budget exhaustion | Host fuzz minimization; extended |
| PXR-04a | Exit 91, mismatched retention or missing PASS abort reduction; no minimality claim | Host fuzz harness health; extended |
| PXR-05 | Unchanged 172038-case sweep, parser controls and UBSan canary | Host regression; extended |
| PXS-01 | clang --analyze and clang-tidy silence on parser sources | Host static/build; extended |
| PXS-02 | Null-dereference canary must emit the analyzer diagnostic | Host static harness health; extended |
| PXB-01 | Parser decode ru_maxrss under 32 MiB observational budget | Host metrics; extended |
| PXB-02 | Dirtied 128 MiB mmap raises RSS at least 64 MiB; undirtied reserve does not | Host metrics harness; extended |
| PXC-01 | Eight forked children decode/reject independently, all exit 0 | Host concurrency; extended |
| PXC-02 | Hang child hits 5-second timeout with complete process-group cleanup | Host harness watchdog; extended |
| PXT-01 | 256 native_exchange rounds, exactly 3072 channel_raw calls | Host transport stress; extended |
| PXT-02 | Invalid size poisons without further channel_raw | Host transport fault; extended |
| PXA-01 | Pinned Clang ASan empty main deadlocks; sample has AsanInitInternal/LockSlow | Host sanitizer inventory; extended |
| PXA-02 | Pinned Clang UBSan empty main exits 0 | Host sanitizer contrast; extended |
| PXA-03 | Apple clang ASan empty main exits 0 (comparison only, not a pin) | Host sanitizer inventory; extended |
| PXA-04 | Pinned ASan heap canary times out without AddressSanitizer output | Host instrumentation health; blocked |
| PXM-01 | JSON matrix lists every PX* ID with family/layer/stage/oracle/evidence | Host documentation/inventory; extended |
| PXM-02 | ASan compensation names NB-01–04, does_not_cover host heap OOB, waiver false | Host documentation/inventory; extended |
| PXM-03 | Mutants marking PXE-04 pass or overclaiming compensation are rejected | Host inventory harness; extended |
| PXM-04 | Unexercised TC-02 families have explicit exclusions | Host documentation/inventory; extended |

Reduction tries nonzero-to-zero substitutions from the end, then single-byte
deletions from the start, and repeats until one full pass of both finds no
further same-oracle failure. That is local minimality for those operations,
not a globally smallest input.

This is a deterministic byte sweep plus local reduction, not coverage-guided
fuzzing or exhaustive parser correctness. The source contains the three fixed seed
records; an oracle failure reports seed/offset/value to reproduce the mutation.
Sanitizer-only crashes still require separate input isolation. Source/plan changes
invalidate reuse of prior evidence.

Darwin does not accept setrlimit of RLIMIT_AS or RLIMIT_DATA on this host. RSS
budgets are observational getrusage checks, not kernel enforcement. Hang cleanup
is harness health, not product recovery.

Pinned Homebrew Clang 21.1.8 ASan deadlocks during InitializeShadowMemory on
macOS 27 (dyld mapping walk mallocs into ASan init). `check-asan-host.py`
records that stack. Apple clang ASan empty main works here and is comparison
only; it is not a pin substitute. PXE-04 stays blocked on the pinned toolchain.
Host UBSan plus existing native denial/reclaim witnesses remain compensation,
not a memory-safety proof or waiver.

The maintainer owns triage and the manual weekly extended cadence in
[PROCESS](../../docs/quality/PROCESS.md). No automation is installed. Remaining
UL-062 work: ASan on a compatible pinned toolchain/OS, kernel RSS enforcement,
broader corpora/schedules, independent review and the weekly cadence. Host SDK
settings/runtime hashes do not pin every host system dependency. Leak detection
is disabled; no leak or native safety claim follows.
