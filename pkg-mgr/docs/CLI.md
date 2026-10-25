# Private-root CLI

The [pkg-mgr(1) manual](../man/pkg-mgr.1) is the command/option reference.
This page supplies workflow, recovery and implementation-validation context.
Registration examples use a private root beneath this checkout because current
evidence-bound registration rejects an external root.

`bin/pkg-mgr` is the first-party POSIX shell entry point over the existing state,
binary and retained-replacement helpers. It adopts the pinned
[Aether Experience](EXPERIENCE.md) contract for this surface. Run it from the
checkout; installing a standalone executable is not implemented.

## Start and inspect

Root creation and builds remain explicit make operations:

```sh
fixture_root=$(mktemp -d "$PWD/.pkg-mgr-live-manual.XXXXXX")
make -s -f mk/pkg.mk ROOT="$fixture_root" init-root
make -s -f mk/pkg.mk ROOT="$fixture_root" register
bin/pkg-mgr --root "$fixture_root" list
bin/pkg-mgr --root "$fixture_root" files hello-local
bin/pkg-mgr --root "$fixture_root" --plain verify
bin/pkg-mgr --root "$fixture_root" --format tsv owners
```

`--root` must identify an absolute, initialized private root. Global options
precede the command. `--help` lists all commands; `--version` identifies the
prototype. Inspection includes `list`, `owners`, `verify`, `orphans`, `files NAME`,
`deps NAME` and `rdeps NAME`.

## Binary and replacement operations

The CLI forwards these arguments to the documented helpers without changing
validation or publication authority:

| Command | Arguments after command | Contract |
| --- | --- | --- |
| `export` | `NAME` | [Binary transport](BINARY-PACKAGE.md) |
| `import` | `BUNDLE BUNDLE-SHA256 TARGET` | [Binary transport](BINARY-PACKAGE.md) |
| `recover` | `BUNDLE BUNDLE-SHA256 TARGET` | [Import recovery](IMPORT-RECOVERY.md) |
| `preflight` | `BUNDLE BUNDLE-SHA256 TARGET` | [Read-only comparison](UPDATE-PREFLIGHT.md) |
| `prepare` | `BUNDLE BUNDLE-SHA256 TARGET OLD-RECORD-SHA256` | [Retained replacement](REPLACEMENT-POLICY.md) |
| `finish` | `INTENT-SHA256` | [Retained replacement](REPLACEMENT-POLICY.md) |

Bundle paths are absolute. Digest and target arguments are explicit caller pins;
local integrity checks do not establish remote authenticity. `prepare` reports
an intent digest and leaves a pending transaction. Save that digest: `finish`
requires it. Normal inspection and mutation remain blocked while replacement is
pending. A successful preflight performs no replacement.

## Output and exit behavior

- `--format human` is the default: results go to stdout; operation status and
  diagnostics go to stderr. Inspection success has no extra status chatter.
- `--format tsv` preserves the helper's stdout, stderr and exit status exactly
  during ordinary completion. Diagnostics remain diagnostics, not TSV records.
  Use this mode for scripts; human wording is not a parsing contract.
- `--quiet` suppresses start/success status, preserving results and failures.
- `--color auto|always|never` controls stderr status labels. Auto requires that
  stderr is a terminal, `TERM` is not `dumb`, and `NO_COLOR` is empty/unset.
  Explicit `always` overrides `NO_COLOR`. Stdout remains uncolored.
- `--plain` uses ASCII output, escaping non-ASCII bytes and control characters
  in human results/diagnostics. Machine mode preserves the original bytes.
  `--plain` or `--format tsv` combined with `--color always` is a usage error.
- Conflicting repeated valued options and control characters in arguments are
  rejected. Both `--option=value` and `--option value` are supported.

Hearth's terminal fallback uses the terminal's default foreground/background,
yellow for running/blocked status, green for success, and red for failure.
Labels carry meaning without color. Human output escapes control bytes; plain
mode additionally escapes high bytes as `\xNN`. There are no animations,
spinners, width-dependent tables, RGB theme overrides, or TUI. `--progress` and
`--verbose` are not implemented for this bounded surface.

Exit codes are `0` success, `1` helper failure, `2` blocked preflight, and `64`
invalid CLI usage. Other helper exit codes pass through. A successful `prepare`
means preparation completed, not that the new package is active.

Output is buffered in a temporary directory until the helper returns. Signals
caught while waiting for the foreground helper are recorded. After the helper
returns, the CLI emits its buffered receipt and diagnostics before reporting
completion as unknown and exiting `130` (INT),
`129` (HUP), or `143` (TERM). It does not promise cancellation, rollback, or
termination of all helper descendants. Inspect state before retrying; pending
replacement requires the pinned finish procedure. These interruption messages
are wrapper diagnostics even in machine mode. A wrapper-only signal does not
forward to the helper: the helper can finish, and the CLI waits for it. A signal
to the entire foreground process group also reaches the helper; the result
depends on its own signal behavior. The first caught signal selects the wrapper
exit code. SIGKILL cannot be trapped and can lose buffered output or leave scratch
files. Closed output pipes and caught rendering interruptions now retain the
raw buffers as described below. No concurrent-writer coordination
or power-loss durability is added.

## Failed output delivery

If stdout/stderr delivery fails, or a caught signal interrupts rendering, the CLI
keeps its private mode-0700 `pkg-mgr-cli.*` directory under `${TMPDIR:-/tmp}`.
It contains raw helper `out`, raw helper `err`, and numeric `helper-exit`.
Working stderr receives an UNKNOWN diagnostic with the retained location. If
stderr is also broken, inspect that temporary parent for the retained directory.
An unreadable start-status stream can stop a command before its helper runs;
such a directory may be empty. Successful delivery normally removes the buffers.

Delivery failure returns `1`, including when the helper returned `0` or `2`.
A caught INT/HUP/TERM keeps precedence as `130`/`129`/`143`. Thus a CLI failure
can follow a completed mutation: do not blindly retry. Ordinary machine-mode
streams and helper exit codes are unchanged when delivery succeeds. Delivery
failure diagnostics are wrapper text even in TSV mode.

The retained files are observations, not package authority. Inspect escaped human
output or use a text viewer that does not execute terminal controls; raw buffers
can contain untrusted bytes. Recover the emitted intent digest and use the normal
pinned `finish` procedure, which revalidates transaction state. Never treat a
retained receipt as permission to bypass those checks. Copy needed evidence to a
chosen location before temporary-file cleanup; remove only that receipt directory
when it is no longer needed. There is no automatic receipt pruning or durability
guarantee. A later filesystem write failure, SIGKILL, or system crash can still
prevent retention. A pipe write accepted by the OS does not prove its reader
consumed the entire result.

## Validation and boundaries

`sh tests/check.sh` includes CLI argument, stream, color, control-escaping,
exit-code and pending-guard checks; binary fixtures exercise blocked preflight
through the CLI. The opt-in `tests/zlib-integration.sh` uses it for actual
export/import, preflight, prepare, repeat finish and final verification of the
zpipe 0.1 to 0.2 replacement. Existing helper interruption tests remain the
transaction evidence; wrapper-wide signal cancellation is not established.

`sh tests/cli-interruption.sh` uses Python only as a development signal driver.
It copies the actual CLI/renderer into a disposable checkout and substitutes a
controlled shell helper, with a FIFO marking a known waiting point. Twelve cases
cover INT/HUP/TERM sent to the wrapper alone and to its isolated process group,
in human and TSV modes with quiet enabled. They assert exit codes, preserved
receipt/diagnostics, no success label, pending fixture preservation, scratch
cleanup and whether the helper continued. The fixture's pending file and intent
string are synthetic; this does not establish transaction validity. The harness
first reproduced receipt loss in the old wrapper. [Evidence](evidence/cli-interruption-2026-09-05/README.md)
records the fix and its limits.

`sh tests/cli-output.sh` adds eighteen controlled cases for closed stdout,
closed stderr, both closed, and INT/HUP/TERM during large-result delivery, in
human and TSV modes. It verifies complete retained raw bytes, private-directory
permissions, helper exit status, nonzero CLI outcome and unchanged synthetic
pending state. [Output failure evidence](evidence/cli-output-2026-09-05/README.md)
records this host-only boundary. The binary fixture now also runs
`tests/cli-receipt.py` against the actual transaction engine: failed prepare
output retains a matching intent digest, a forged digest is rejected, failed
finish output retains its completed receipt, and repeated finish verifies the
completed state. Both human/closed-stdout and TSV/both-closed workflows preserve
unrelated records, world and the retained old package. [Transaction receipt evidence](evidence/cli-receipt-2026-09-05/README.md)
records this synthetic-package, actual-engine acceptance check.

No live-prefix install, removal, service activation, remote repository access,
solver, or native Aether execution is introduced. Legacy helper output retains
its migration exception. Shared normative changes belong in Aether-standards;
this document defines only this consumer's implementation.

## Dispatch contract coverage

`python3 tests/cli-dispatch.py` checks all 13 public commands against an independent
helper/argument table. Thirty-nine routing/status cases preserve exact TSV streams
and statuses 0/2/73; 22 invalid argument counts reject before helper invocation.
Quoted paths remain single arguments and each case checks temporary cleanup.
Controlled helpers establish wrapper dispatch only; populated package state and
actual transaction authority remain the responsibility of the integration fixtures.
[Evidence](evidence/cli-dispatch-2026-09-07/README.md) includes mutation controls.

The package-state fixture also invokes `tests/cli-populated.py` on its registered
base/app/spare state. Seven read-only views compare exact helper streams/status;
missing-package and mode-drift cases check exact failure output. Every call preserves
entry paths/types/modes and payload/record hashes. This fixture is part of
`sh tests/check.sh`; it is not an operator command for arbitrary package roots.
[Populated-state evidence](evidence/cli-populated-2026-09-07/README.md) records this
actual-helper boundary without claiming native or mutating-command acceptance.

The binary-package fixture exercises CLI export/import with base/app artifacts
and exact machine receipts. CLI recovery adopts a copy of a genuinely interrupted
fixture stage, verifies its records/payload and repeats without changing the file
snapshot. Original helper interruption tests remain in place.
[Binary CLI evidence](evidence/cli-binary-2026-09-07/README.md) records this private
root acceptance; it is not a native persistence or repository trust witness.
