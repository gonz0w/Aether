# Runtime test strategy

2026-09-05. BG-017 research result and acceptance plan. [Decision 0002](../decisions/0002-runtime-model-profile.md) records semantic review and the first executable-model scope. The subsequent [BG-053 results](../RUNTIME-MODEL.md) record passing model coverage. Host/transport/VM cases below remain planned unless separately evidenced.

## Layers and proof boundaries

| Layer | Technique and evidence | Cannot establish |
| --- | --- | --- |
| Static inputs | Parse bounded definitions; validate names, references, evidence kinds, required policy support and graph cycles without side effects | Launch, authority or timing correctness |
| Deterministic model | Fake clock, injected effects/completions, hand-authored traces, bounded event permutations; save counterexample input and state/effect sequence | OS scheduling, signal delivery, descriptor inheritance, actual reclaim |
| Real host children | Foreground fixtures with pipe handshakes, exit/fault/blocked-writer cases and explicit reap; record platform/runtime | Arbitrary descendant containment, PID 1 adoption or native Aether behavior |
| Isolated VM | Guest init/service startup, guest shutdown and boot-failure controls; versioned serial markers and independent watchdog | Every hardware/driver failure or all race schedules |
| Native Aether fixture | Existing external client and two negative controls, pinned source and artifact hashes | General readiness, clocks, arbitrary services or production recovery |

Standard-library [unittest](https://docs.python.org/3/library/unittest.html) supplies isolated fixtures, discovery and failure reporting without another package. The [QEMU monitor](https://www.qemu.org/docs/master/system/monitor.html) supplies guest-control/debug facilities; VM liveness still needs an independent watchdog and expected guest evidence. These primary manuals were reviewed, not used to claim new test results. The POSIX wait manual fetch was unavailable; real-child ownership semantics require source verification in BG-054 before implementation. Existing [native evidence](../LIFECYCLE-V1.md) is the executed target baseline and should not be relabeled as model or host coverage.

A fake supervisor should expose incomplete operations, not merely return success. Maintain separate requested effects and observed results, inject denied/exhausted/late outcomes, and require explicit cleanup acknowledgments. Record the earliest failing trace with seed, graph and simulated timestamps. Deterministic enumeration and a fixed seeded stress corpus complement each other; random sampling is not exhaustive verification.

## Requirement-to-case matrix

M means deterministic model, H real host fixtures, V isolated VM/native profile when supported. Each row is a future case family with explicit expected outcomes.

| Case | Requirements | Layer | Input and oracle |
| --- | --- | --- | --- |
| T01 Identity reuse | R-01, R-09 | M/H/V | Old epoch/generation event after replacement: no current readiness or control effect |
| T02 Honest state | R-02, R-03, R-17 | M/H | Launch accepted then observation lost: status unknown/pending, never inferred absent or ready |
| T03 Invalid graph | R-04, R-05, R-08 | M/H | Missing edge, cycle, invalid evidence or unsupported hard policy: zero launch effects |
| T04 Ordering-only rejection | R-05 | M | Provider rejected before launch: after-only consumer may proceed; requires consumer remains blocked |
| T05 One-shot reuse | R-06 | M/H | Two starts in same session reuse completion; stop invalidates it; later start reruns once; new epoch never inherits it |
| T06 Evidence selection | R-06, R-09 | M/H | Started cannot satisfy notified-ready; reject incompatible provider declaration before launch |
| T07 Batch precedence | R-07, R-09 | M | Permute ready/terminal/stop/deadline in one cut: no ready-dependent admission when disqualifying evidence is known |
| T08 Later failure | R-07 | M/H | Provider fails in a later cut after consumer dispatch: consumer retained, dependency loss reported, new admission blocked |
| T09 Restriction rollback | R-08 | M/H | Fail each setup step: no unrestricted launch; acquired resources released or cleanup failure retained |
| T10 Readiness transport | R-09, R-18 | H | EOF, partial/oversized frame, leaked writer, early notification: match selected BG-040 framing/authority contract with bounded processing |
| T11 Retry accounting | R-10, R-11 | M/H | N=2 gives at most three launches; successful exit never retries; ready never resets N; denied policy never retries |
| T12 Retry after activation | R-11, R-15 | M | Completed start followed by fault: desired-running policy retries; repeated start cannot replenish budget |
| T13 Deadline cleanup | R-12 | M/H | Expire activation with one successful service and one initializing provider: cancel queued work, retain successful service, stop/reclaim initializing provider, expose dependency loss |
| T14 Stop rejection purity | R-13 | M | Required consumer outside stop scope: all state/timers unchanged; return conflict and scope explanation |
| T15 Stop/restart ownership | R-13, R-14 | M/H | Consumer first; cleanup failure prevents replacement; one-shot/absent restart rejected without effects |
| T16 Late launch | R-15, R-16 | M/H | Stop supersedes start, completion arrives later: owned generation reclaimed, no resurrection |
| T17 Client timeout | R-15 | M/H | Timeout/disconnect/replayed ID: operation remains owned, no duplicated launches; exact replay scope waits for BG-050 |
| T18 Partial graph result | R-12, R-15 | M | One participant permanently fails: terminal operation reports partial results and retains successful services; no implicit rollback |
| T19 Experiment shutdown | R-16 | M/H/V | Close admissions; inventory all owned fixtures; never emit host-wide kill/reboot action |
| T20 Diagnostic isolation | R-17, R-18 | M/H | Malicious service text cannot change identity; stalled sink/subscriber cannot block lifecycle effects; drops counted |
| T21 Bounds and clock jumps | R-09, R-11, R-18 | M | Reject graph/event limits; jump past deadlines without extending them; bounded retained events and deterministic output |

T10/T17 cannot pass merely because a model accepts synthetic authorized events. Identity authentication, framing and deduplication are separate host/transport obligations. Model coverage of a requirement is partial until its real mechanism is tested.

## Experiment procedure and controls

BG-053 implements T01–T09, T11–T16 and T18–T21 to the model extent in decision 0002. Keep expected effects explicit in test fixtures. For T07 enumerate permutations only inside one declared observation cut; separately test failure in a later cut with the different correct outcome. Initial bounded exploration is not a mathematical proof of all event schedules.

Require negative controls that alter readiness-generation checking, permit retry-budget reset and bypass cleanup gating. Each deliberately defective behavior must be caught by an existing independent expectation. Do not ship mutant behaviors as runtime options; use temporary test substitutions or isolated copies. A broken harness, missing runner or zero discovered cases must fail validation rather than look green.

Host fixtures later use explicit child-to-parent synchronization rather than sleep-based ordering. Give each case a hard external watchdog, temporary output directory, owned PID inventory and cleanup on failure. Never use process-name matching, broad kill(-1), host shutdown or privileged PID 1 experiments. A process group may assist test cleanup but does not prove containment of arbitrary escaping descendants. Failed teardown is a test failure. Inject launch/exec denial, reader death, full output pipes, hung readiness and late exits under the supported host profile.

Test shell fixtures with the selected POSIX shell's syntax checker before execution; use ShellCheck where installed and record its version/availability. Static shell checks do not validate process ownership. No shell runtime exists in this change, so no shell check is claimed here.

Native tests retain isolated source snapshots, compiler/tool versions, envelope hashes, positive versioned markers and semantic negatives. QEMU boot failure or infrastructure timeout must not satisfy a negative semantic test. Run target checks when native client/ABI assumptions change, not on every documentation edit.

## CI and measurement plan

BG-054 owns CI implementation: first a Python standard-library model job, then macOS and Linux real-child jobs, then BSD/illumos jobs when reproducible runners exist. Missing runner coverage is reported untested. Native Aether remains an explicit toolchain/boot-asset job; no external account or CI workflow is configured by this research.

Model acceptance bounds are in decision 0002. Capture Python/OS/CPU, fixed workload, elapsed time and peak memory for 1,000 traces. Do not compare model interpreter RSS with native client size. Future host budgets must measure supervisor idle/loaded memory, dependency-to-ready latency, stop/reclaim latency and bounded diagnostic pressure on a documented graph. Publish baseline first; tighten numeric product thresholds with evidence. No performance result is claimed now.

Follow-ons BG-053 (model/fault corpus) and BG-054 (real-child/CI harness) were captured before completing BG-017. BG-040/BG-050/BG-028 remain preconditions for a real host supervisor; BG-032/BG-033 remain native gates. BG-052 completion means the bounded profile has been reviewed and accepted for modelling, not that all runtime semantics are proven.
