# Native exec descriptor composition — 2026-09-10

The actual Rust connection owner now uses the reviewed pure descriptor preparation
routine around native image commit. A real C startup table retains FD1/10 CLOEXEC
across rejected admission; the old image reads a, then b through its FD0/10 aliases.
After successful commit, final binding1 cleanup precedes release of the replacement.
The distinct C ELF installs a checked survivor table, rejects FD1/10, reads c through
FD0 at the retained position, then closes FD0/2. Two generations end with client62,
backend17 and peer17, reclaiming six domains. TLS is present and checked in both images.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#native-exec-descriptor-composition-selection--2026-09-10)
and [native reference](../../NATIVE-CONNECTIONS.md#native-exec-descriptor-composition--2026-09-10)
record owner, authority, bounds, failure ordering and limits. No new native ABI,
service, namespace, dependency, installed SDK or released pin is introduced.
The native kernel source is unchanged; the new modes select the existing bounded
exec, process-copy, memory/freeze and local-runner signal-mask profiles.

## Qualification

The complete171-case connections suite, five launch cases and host suite pass.
Host discovery includes99 Python tests and the five Rust preparation tests. The
new modes have two semantic controls:

| Control | Required observation |
| --- | --- |
| Retain old CLOEXEC table | Replacement216, owner2040, zero reclaims |
| Reset surviving input position | Owner1903, zero reclaims |

The positive demands exact ordered terminal records and six reclaims. A generic
panic, compile failure or timeout cannot satisfy these controls. Existing native
commands in the reference reproduce the complete suite; no new CLI switch is added.
`*-timing.json` records commands, start UTC, elapsed time and exit codes. Per-case
results and raw logs bind selected input/tool/firmware identity and expected oracles.
Selected suites finish within their1800-second review budgets.

`compatibility.json` verifies all168 prior connections payloads outside bootstrap
entropy bytes32..79 and their identical kernel binaries. Command/M4 runs from the
image-gate packet remain historical; they were not rerun for this scoped fixture
and harness change. New source-built native owner code remains within8192 bytes;
`qualification.json` records its suite maximum (6,648 bytes),239 source files and3,251 final target artifact files.

## Preserved attempts

1. `attempt1/`: Rust compilation rejected an ambiguous generation integer used by
   `to_le_bytes`. Made it u32. Review also moved peer allocation before cleanup to
   avoid exhausting channel generations through sequential reuse.
2. `attempt2/`: harness variable reuse caused the existing fork link to omit its
   stage hook. Fixture-specific temporary names restore the original link inputs.
3. `attempt3/`: loader rejected the new C ELF without a nonempty TLS segment. Added
   and checked a TLS cookie; loader validation was preserved.
4. `attempt4/`: source215 because startup mask operations require local-runner;
   peer189 because its bootstrap expected the worker name. The new modes select
   the existing profile and use the correct peer argument.

Host and launch checks passed in each attempt. Each failed connections attempt,
source snapshot and complete generated target directory is retained. No runtime
edits occurred until all processes for that attempt completed. Archive contents
are read back and checked, including failed attempts; none is discarded on retry.

## Limits and next action

A local release obligation is not a global backend-close permission. This fixed
witness has no other process sharing these descriptions: removing FD10 leaves its
same-process FD0 alias alive. The peer backend tests lifecycle/resources only.
Cross-process shared-holder exec remains unqualified.

The32-byte native channel cannot buffer the complete bootstrap while the receiver
is parked. After exact backend-close success, kernel publication releases the
trusted startup receiver. The owner streams bootstrap/table, and the replacement
validates the complete table before application I/O. Kernel execution and descriptor
readiness are distinct. Unknown or incomplete close/bootstrap results reject this
bounded experiment; they do not implement service recovery, replay or old-program
resumption after commit. Deliberate lost-reply containment and cleanup are next.

Live exec signal transitions, stale mapping/reuse witnesses, arbitrary image/path
admission, public execve, installed SDK intake and actual dash acceptance remain open.
This is producer fixture evidence, not a completed shell or R1 release gate.

`sources.json`/`sources.tar.gz` capture final documentation and implementation;
`run-sources.*` preserve the pre-run snapshot. `change.patch` compares the previous
sealed descriptor-preparation snapshot. `artifacts.json`/`artifacts.tar.gz` preserve
all final target files. `final-checks.json` records post-documentation host, scoped
Rust/C formatting, workflow, standards and whitespace checks. The prior manifest
and pinned simplicity digest/four files are verified. `manifest.json` seals every
packet file except itself.
