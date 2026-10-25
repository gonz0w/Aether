# Recurring host-runner handoff

For the homelab runner operator. Status: **prepared locally, not deployed**.
Aether is the only release target. A Linux VM would be a development host and needs
its own executed qualification; existing macOS evidence does not qualify it. No
old Apple installer/VM reconstruction is required. Forgejo URL, VM hostname/OS,
runner identity and schedule installation remain operator inputs.

## Payload and trust boundary

Use a private development source snapshot made by:

```sh
# From the controlled pkg-mgr checkout, after local developer prerequisites exist.
python3 tests/check-source-snapshot.py
```

The printed root retains source.tar, repeat.tar, input-files.json, result.json and
extracted/pkg-mgr. The result supplies the expected archive SHA-256; the embedded
SOURCE-MANIFEST.json binds paths, modes, sizes and source bytes. SECURITY.md is a
required input. The referenced .githooks source tree is included without installing
hooks or creating Git metadata. Missing policy or hook tree fails assembly; never omit it to pass a source check.
The [snapshot contract](SOURCE-SNAPSHOT.md) owns exact assembly/extraction behavior.

Transfer the archive and separately retained result/input manifest through the
operator's chosen private channel. Establish the expected digest from the controlled
source-side receipt before extraction. A digest received beside an untrusted archive
is not independent authenticity. This handoff supplies no remote trust bootstrap or
release eligibility. The source includes historical research/evidence and uncommitted
Origins work from the tested development tree; it is not a public release package.
Do not publish it automatically or label HEAD alone as its complete source identity.

The locally prepared [handoff evidence](evidence/runner-handoff-2026-09-07/README.md)
records the retained artifact paths and exact hashes. The large archive stays outside
Git. It may be copied explicitly once the destination is known; none was sent here.

## Provisioning and qualification

Provision tools separately; do not install packages from a test job. Required host
inputs are POSIX sh, Python 3.10+, GNU Make 3.81+, ShellCheck exactly 0.11.0, normal
Unix text/file utilities and a working SHA-256 provider. The full source extraction
path also needs tar. Install mandoc and man when requiring documentation rendering;
missing optional rendering must stay NOT RUN. Compiler examples, native QEMU and
external zlib archives are separate opt-in prerequisites. Record actual tools,
versions, binary identities and acquisition provenance for the selected VM.

The old check-host-setup.py is explicitly macOS-profile-specific. Do not use it as
a Linux admission gate or infer qualification from version strings alone. Execute
the actual suite on the new host, with a private HOME and writable TMPDIR, no real
installation prefix and no signing/deployment credentials. Tests execute trusted
checkout code. Do not run unreviewed PR code in a persistent privileged runner.
Isolation/network enforcement belongs to the runner operator; this handoff does
not configure or prove it.

Use a frozen source tree per job; do not git pull or modify it while testing. From
the extracted pkg-mgr directory, execute:

```sh
sh tests/check.sh
```

Preserve its raw exit status; a successful log-upload command must not replace a
failed test status. Capture stdout and stderr. The initial line gives the retained
runner root; keep its result.txt, suite.log and nested evidence directories even
on failure. Zero exit alone is insufficient if required receipts/completion are
missing. Executable startup failure returns 125 and retains a failed result.txt
and suite.log when the run directory is writable; an unwritable or full filesystem
can still prevent evidence retention. Do not invoke check-fixtures.sh directly: it bypasses the outer watchdog.

Qualify the actual VM first with one full run and then the five sequential runs in
[TEST-PLAN](TEST-PLAN.md). Each run has its own root and 600-second fixture deadline;
the five-run budget is 3000 seconds. Prevent overlapping jobs for the same source
and resource allocation. Scheduler termination must allow the watchdog to clean its
owned process group and preserve evidence. Forced VM termination is an incomplete
run, not successful cleanup. The existing watchdog cannot confine a child that
intentionally escapes its group; use a disposable VM for uncertain teardown.

## Recurrence and evidence collection

After host qualification and operator setup, the plan is one daily full run and
five sequential weekly/candidate runs. Record the actual schedule, timezone, job
identity, tested source/artifact, triggers, overlap policy and operator in STATE.
No cron entry, Forgejo workflow, runner registration or remote service is installed
by this document. The repository currently has no configured Git remote.

Copy retained evidence to operator-owned storage without altering failed logs.
Record the result of evidence transfer separately: an upload failure cannot yield
a passing qualified job. Preserve input archive/digest, tool identities, UTC times,
command/status, per-run watchdog receipts, full logs, corpus seed and every attempt.
Run evidence remains local until transfer is actually confirmed. No S3 bucket,
immutability or long-term retention service is provisioned here.

Use the seven-day local host evidence age and change-invalidation rules in TEST-PLAN.
Retain active experimental claims; define the support/security retention period
before publication. Missing jobs, missing evidence and flaky failures require triage
and remain visible. The operator must specify who receives job failures; documenting
a security-reporting mailbox does not authorize sending CI notifications to it.

## Completion receipt required from the operator

Return the VM/OS and runner identity; exact source/tool hashes; actual command and
schedule/timezone; run-root/evidence-storage locations; five real results including
failed attempts; timeout/cleanup behavior; evidence-transfer outcome; responsible
operator and triage contact. Keep absent values pending. Only then can ADP04-03
recurring deployment be recorded as executed. Native package/storage acceptance,
independent reader review and release publication remain distinct gates.
