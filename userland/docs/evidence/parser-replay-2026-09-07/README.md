# UL-062 parser replay and reduction — 2026-09-07

Host parser failing-input retention, replay and local minimization now pass on
Python 3.14.7 and 3.10.21 with explicit UBSan. The reserved-byte defect retains
exact 224-byte input and `canonical-carrier` metadata, replays at exit 90, and
the unchanged parser accepts the same bytes. Reduction zeros nine trailing
argument bytes and then reports local minimality for single-byte deletion and
nonzero-to-zero substitution (498 oracle calls). Synthetic deletion stops at two
zero bytes, zero reduction stops at `0x03`, a non-reproducing seed is refused,
and a 1-call budget fails without writing a claimed minimum. Empty, 225-byte,
226-byte, missing and invalid-expectation replay paths use exit 91 or a passing
reject as specified. Exclusive `failure.bin`/`failure.json` collisions leave the
original sentinel bytes. All owned process groups in the passing runs complete
cleanup. No production parser, native contract, sibling repository or release
pin changed.

This directory began as an implementation handoff after an app security-screening
message; [handoff.json](handoff.json) and the earlier README text recorded
unvalidated `parser-extended.c` edits and missing driver work. Those edits were
reviewed, compiled and executed here. The first reduction order exhausted the
1024-call budget while zeroing trailing argument bytes after a full deletion
scan each iteration; that incomplete attempt is retained. The passing driver
tries nonzero-to-zero from the end, then deletions from the start.

Default ASan/UBSan mode was not rerun. PXE-04 remains blocked on this host.
Sanitizer-only crash isolation, transport/concurrency stress, static analysis,
RSS budgets, native compensation and independent review remain open. This does
not close UL-062.

See [PLAN.md](PLAN.md) and [change-review.md](change-review.md) for predeclared
oracles and [EXTENDED.md](../../../experiments/command-runner/EXTENDED.md) for
commands, private-cwd rules and recovery. Built binaries remain in the named
build directories; hashes are in each summary. Apple SDK settings/path are
recorded; complete host system dependency closure is not claimed.

| Attempt | Result |
| --- | --- |
| parser-extended-6obs5d2y | Python 3.14.7, deletion-first reduction: budget exhaustion; cleanup complete |
| parser-extended-pd50oio3 | Python 3.14.7, explicit UBSan: pass |
| parser-extended-1d_f6uwp | Python 3.10.21, explicit UBSan: pass |

Sweep discovery remains 172038 checks (17550 accepted, 154488 rejected). Passing
suites recorded 544 owned commands each. These durations are observations, not
throughput guarantees. Independent technical review is pending; no reader or
release approval is inferred. Retain all attempts under the project's evidence
policy.
