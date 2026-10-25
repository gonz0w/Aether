# Offline development checks

In the consolidated repository, `python3 scripts/check-all.py --current` selects
current source and host gates while explicitly omitting historical native bundle
replay. Its report records `historical_native_evidence: not-run`; it cannot qualify
native behavior or a release. The default command retains its full historical
audit and fails on missing bundle members. Root `make check-init` uses `--current`
so ordinary development does not require retained binary test archives. Root
DEVELOPMENT's compact retention policy applies; do not regenerate historical pins.

Run from any directory with a POSIX host, Python 3.10 or later, and installed
Rust 1.98.0 (discoverable through rustup):

```sh
python3 scripts/check-all.py
```

The relative example assumes the repository root; an absolute script path also
works. No third-party Python packages, container daemon, network fetch or sibling
checkout is needed. Python remains a development dependency, not the selected
production init language. The existing host adapter requires POSIX process and
descriptor facilities; native Aether checks remain separate.

Each invocation creates a private `out/checks/run-*` directory. Use
`--output-root PATH` to select another parent. Existing evidence is never reused
as this run's result. The directory contains `results.json`, per-check stdout and
stderr logs, and `model.json` when the model ran. The host JSON is `host.stdout`.
Retain the entire directory as a CI artifact, including failed runs.

Order: verify pinned Foundations, Experience and Distribution; audit the pinned
quality review snapshot and local coverage records with
`python3 scripts/check-quality-process.py`; audit the pinned
historical native evidence catalog (without target execution); run harness
evidence regressions; run synthetic host Rust sample-receipt tests; run the deterministic model with mutation controls and its
exploratory baseline; run trusted foreground-child/descriptor tests. The first
failure stops execution and lists later checks as `not_run`. Required empty,
partial or skipped test suites reject. Each command has a 60-second watchdog;
the model and host runners retain their own 30-second watchdogs. Missing commands,
nonzero exits and timeouts have separate result labels.

The outer watchdog kills its own process group. The host suite uses its own
session and watchdog; this is not general descendant containment or proof of
cleanup after machine failure/SIGKILL. Fixtures must remain trusted and bounded.
SIGINT during a check kills its owned group and records interruption. No service
is installed or launched from distribution configuration.

The versioned report `sys-init-development-checks-v1` records host, architecture,
Python/executable, working directory, source and pin-manifest SHA-256 values,
exact commands, elapsed seconds, exit codes and log filenames. Source hashes are
compared before/after the run; a detected change prevents success. This detects
ordinary concurrent edits, not malicious edit-and-restore races. Pin check logs
prove integrity of release bytes separately. Native status is always `not-run`.

stdout is one JSON object with `schema`, `result` and absolute `report` path;
stderr carries plain ASCII progress. `--help` and `--version` use stdout, exit 0.
Exit 0 means every required check passed; 1 means operational/check failure;
2 means an unsupported host; 64 means invalid usage; recorded SIGINT returns 130.
Unexpected interpreter/filesystem failure can prevent a final report; `running`
or absent reports are never passing artifacts. These are developer check
contracts, not the future operator CLI.

## Historical host evidence and CI boundary

Other-OS product qualification is retired. The table records dated development
results only; unrun BSD/illumos hosts are not product blockers.

| Environment | Status on 2026-09-05 |
| --- | --- |
| macOS arm64, current Python | Combined command tested: 34 model cases, three mutation controls, 38 host cases and 14 harness evidence/runner cases |
| Linux | Full suite passes in cached Podman Linux aarch64 image; [exact evidence](evidence/host-diagnostics-linux-2026-09-05/README.md) |
| FreeBSD / other BSD hosts | Not run |
| illumos | Not run |
| Native Aether | Separate earlier lifecycle fixture; excluded from this command |
| Hosted CI | Not configured or executed; checkout has no configured Git remote/provider |

A provider can invoke this same command and upload its output directory even on
failure. No additional platform matrix is required. Each host result records its actual
OS/architecture/Python and required cases; skipped checks cannot qualify that run. No unverified hosted workflow or mutable container tag
is introduced. BG-054 retains development harness and parent/helper ownership work.

Runner regressions exercise missing executables, explicit exit 7 with both logs,
timeout, successful execution, empty/skipped/partial suites and CLI contracts.
An isolated copy with the evidence test files removed exits 1 after standards
verification, with model/host explicitly not run. This is harness failure
evidence, not an expected runtime semantic rejection.

Applicable shared requirements are pinned [Foundations E-01–E-08](vendor/aether-foundations/v0.1.0/EVIDENCE.md)
and [Experience command/output rules](EXPERIENCE.md). Shared standards and pins
are unchanged. Results apply only to the recorded host; timings are exploratory,
not comparative performance claims.

Retained [passing report](evidence/development-checks-2026-09-05/positive/results.json) and [empty-suite report](evidence/development-checks-2026-09-05/empty-suite-control/results.json) include adjacent logs. Paths in the negative report name the disposable snapshot at execution time, which has since been removed.

The later [host deadline follow-up](decisions/0004-host-request-clock.md) raises current host coverage from 20 to 24 cases. Its [combined report](evidence/host-deadlines-2026-09-05/positive/results.json) supersedes the earlier passing snapshot for current adapter code; both snapshots are retained.

The [emergency cleanup follow-up](decisions/0005-host-emergency-close.md) raises current coverage to 30 host cases. Its [combined report](evidence/host-cleanup-2026-09-05/positive/results.json) records the current adapter and all discovered host test source hashes. Earlier reports remain historical snapshots.

[Parent-death witnesses](decisions/0006-host-parent-death-witness.md) raise current host coverage to 32 cases. The [latest combined run](evidence/host-parent-death-2026-09-05/positive/results.json) includes normal cleanup and expected child survival after abrupt supervisor death. Passing this survival test explicitly does not establish containment.

The [terminal-accounting follow-up](evidence/host-accounting-2026-09-05/README.md) raises current host coverage to 35 cases and retains the latest combined report. The new tests cover accumulated exits, real exec failures and post-construction executable changes.

[Exclusive-wait/helper tests](decisions/0007-host-exclusive-wait.md) raise current host coverage to 38 cases. The [combined run](evidence/host-wait-ownership-2026-09-05/positive/results.json) records the direct-wait adapter fix and its regression tests; see its linked snapshot note for concurrent native work.

Run the separate [host measurement command](HOST-MEASUREMENTS.md) with `python3 scripts/measure-host-runtime.py`. Its three summary tests join the evidence suite (13 current harness tests); workload timings stay outside the functional check gate.

The native I/O stop harness adds an SDK receipt/payload/profile validation test (14 current harness tests). Actual target execution remains separate; see [the stop evidence](evidence/native-io-stop-2026-09-05/README.md).

The [native evidence audit](NATIVE-COVERAGE.md) is also available separately with
`python3 scripts/check-native-evidence.py`. It reads only pinned historical
artifacts, returns a JSON result with `native: not-run`, and fails when required
cases, identities or semantic markers do not match. It does not replace QEMU
integration tests. Help/version exit 0, invalid usage 64, audit failure 1; failures
use stderr. The catalog itself is included in the full runner's source hashes.

Linux checkpoint: [decision 0016](decisions/0016-linux-host-validation.md) runs a
frozen source snapshot in the existing cached image without network or pulls,
with read-only source/root and bounded resources. Both macOS and Linux pass 48
host cases. This is actual consuming evidence, not a CI-provider setup. BSD and
illumos remain unexecuted; see [integration gates](INTEGRATION-GATES.md).

## Required receipt-validator gate — decision 0078

The ninth gate, `sample-receipts`, compiles the pure allocation-free Rust
receipt validator on the host with Rust 1.98.0/edition 2024. The wrapper first uses
`rustup which --toolchain 1.98.0 rustc`, then invokes that installed compiler
directly. It never installs a compiler or fetches a dependency. An absent compiler
fails this required gate; provision it separately before offline work. This is a
development-tool prerequisite for testing intended native Rust logic,
not a selected POSIX runtime dependency or production language.

Nine named Rust tests include parameterized malformed/partial/terminal cases.
Two separately compiled omission controls must fail their exact named assertions.
The three Python wrapper cases reject missing test names, zero/skipped tests,
wrong compiler version, nonzero builds or unexpected control results. Each tool
call has a 20-second deadline inside the existing 60-second gate watchdog.
Artifacts remain in private `out/sample-receipts/run-*`: copied Rust inputs,
compiler path/version/hash, exact commands, statuses and stdout/stderr logs.
The full-check record also hashes both Rust files and the Python wrapper.
The existing stdout JSON/exit contracts and plain stderr progress remain; the new
stage name is `sample-receipts`. No native Aether behavior is exercised by this gate.
Prior Python-only and platform pass records apply to their frozen snapshots.


Decision 0085 extends this same gate with three named host pending-view tests
and a separately compiled token-omission control. The wrapper now runs five
Python cases: the original three plus pending-view positives and its control.
Both additional Rust files (`pending_history.rs` and `native_pending_history.rs`)
are copied into the private run and hashed by check-all. Compiler lookup, deadlines,
offline behavior, original tests and machine contracts remain unchanged. These
host checks establish synthetic comparison logic; private bound native capture
still requires the separate consuming witness.


Decision 0086 expands the pending-view suite to nine named view/conflict tests
and adds four separately compiled conflict controls. Together with the existing
nine sample tests and three earlier controls, the same gate now runs nine Python
wrapper cases. The completeness guard is updated to nine; tool deadlines,
compiler pin, source hashing, offline behavior and output contracts are unchanged.
Local closure and immutable borrowed retention remain host claims until a native
guard consumes the new core.

## Required static gate — decision 0095

The aggregate now includes `static`: [scope and tooling](STATIC-CHECKS.md).
Python syntax and two pinned host Rust formats are required. Unsupported tool
identity/host is blocked, never skipped into success. Existing native-source
bytes and markers remain unchanged; historical nine-gate reports stay historical.

The canonical [source manual](man/sys-init-checks.1) covers aggregate command
options, exits, environment, artifacts and offline prerequisites. Render it with
`mandoc -T ascii docs/man/sys-init-checks.1`; this is not installed-target lookup.
See [documentation coverage](DOCUMENTATION-INVENTORY.md) for review status.

Decision 0108 caps each aggregate gate's combined stdout/stderr logs at 4 MiB.
Capture preserves separate raw prefixes and reports output-limit independently
of timeout or a child test failure. The 60-second deadline covers pipe draining
and process exit. Child artifacts/hash work and detached nested groups remain
outside these bounds. See docs/man/sys-init-checks.1 and decision 0108.

Decision 0110 adds a one-second cooperative SIGINT grace before aggregate
forced cleanup, allowing responsive Python wrappers to reap separate-group
workers. The grace is additional to the gate deadline; failure identity and
log caps remain unchanged. Forced fallback covers the owned gate group only.
Unresponsive detached descendants, abrupt outer termination, deeper nesting
and pipe pressure remain explicit limits. See decision 0110 and its regression.

Decision 0111 routes SIGTERM during active main-thread aggregate capture through
the interrupted result and cooperative cleanup path, restoring the previous
handler afterward. Secondary SIGTERM during cleanup is ignored. Startup,
between-gate work, SIGKILL, repeated SIGINT and detached/deep nesting remain
outside this guarantee. Background-thread calls keep prior signal behavior.
See the aggregate manual and retained real-signal before/after witness.


## Aggregate source snapshots — decision 0143

Before/after source maps keep the existing selected Python, explicit input, lock
and vendor-manifest paths. Snapshot traversal now excludes archive directories,
rejects symlinks/special entries under scanned roots, and permits at most 200,000
entries and 10,000 selected files. Files are ordinary with a 4 MiB per-file and
64 MiB total limit; SHA-256 reads use 64 KiB chunks. Components at/below checkout
root, descriptor identity before/after reads and final path identity are checked;
selected membership is checked again after hashing. Descriptors close on errors.
Successful source_sha256 keys/values remain compatible with the old algorithm.

These sequential checks are not atomic snapshots or filesystem I/O deadlines.
Ancestors above checkout root are outside scope. Snapshot failure reporting and
report publication outside an active gate retain existing behavior and remain
separate review work. Native source, receipt schemas and release pins are unchanged.


## Report publication and snapshot failures — decision 0144

Reports are written to an owned temporary file in the run directory and replaced
atomically; temporary files are removed on failure. This prevents partial JSON
replacement, not power-loss durability (no fsync promise). A running report is
published before the initial snapshot. Expected I/O/validation failures and
KeyboardInterrupt preserve completed checks, set sources_unchanged=false and
record not_run. Failed reports may add error with stage, type and a message bounded
to 4,096 characters. Initial snapshot failure leaves source_sha256 empty. Stages
are initial-report, initial-snapshot, snapshot-report, gate:<name>, gate-report:<name>
and final-snapshot. This additive failure detail leaves successful fields unchanged.

A terminal stdout summary is emitted only after final report publication succeeds.
Interrupted runs return 130; other failures return 1. If final publication itself
fails, stderr receives an escaped diagnostic and no terminal summary is emitted;
the prior complete report may remain running. Gate logs survive. Output-directory
creation, repeated/fatal signals, broken output pipes and filesystem I/O deadlines
remain separate limits. Active-gate cleanup remains owned by run_check.


## Startup and output delivery — decision 0145

Output-root/private-directory creation errors now return 1 with escaped stderr;
KeyboardInterrupt returns 130. No report path or result summary is invented when
startup fails. The existing output-root resolution/symlink policy is unchanged.

Terminal summaries are flushed before returning. An output OSError returns 1
(or preserves 130 for interruption) and reports summary delivery failure on stderr
where possible. The already-published report retains its check result: completed
checks are not undone by terminal delivery failure. A progress OSError records
stage gate-progress:<name>, preserves the completed gate and stops later gates.
Failed output descriptors are redirected to os.devnull where possible to avoid
buffered errors at interpreter shutdown. Diagnostic output is best effort when
stderr itself is unavailable. No global signal disposition changes.

Fatal/repeated signals, blocked I/O, failed descriptor redirection and crash
durability remain limits. Real closed-pipe tests use bounded, private stub gates;
they do not execute native code or modify historical evidence.


## Optional extended host campaign — decision 0147

`python3 scripts/check-extended-host.py` runs EHT-01 separately from the ten gates.
Eight seeded fresh workers each execute all 54 pinned host cases; `--seed` replays
one plan seed. Parent/worker identity and actual-order/count checks reject missing,
skipped or contradictory evidence. Reuses bounded gate capture and atomic report
helpers, with 60 seconds/4 MiB per worker and 600 seconds/campaign. See
EXTENDED-HOST-TESTS.md and the command manual for outcome/cleanup limitations.
No scheduling, native execution or broader platform qualification is implied.
