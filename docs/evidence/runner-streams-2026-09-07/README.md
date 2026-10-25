# Runner output roles — 2026-09-07

AEOUT001 is an explicitly selected runner-only fixture with separate stdout and
stderr write/close grants, bounded to 512/256 bytes. A separate Rust backend owns
both sinks and immutable input; the Rust owner independently verifies exact bytes,
lengths, EOF, explicit closes and two-generation native cleanup. The C client
exercises actual musl write/close using copied proposed help/version/usage text.
It does not implement runner argument parsing or assert a released version.

See the [preimplementation contract](contract.md) and
[NATIVE-COMMAND-IO](../../NATIVE-COMMAND-IO.md) for field layout and scope. No new
kernel ABI, capacity, pin or sibling modification is part of this change. Existing
child bindings and startup profiles remain separate. All original code is
BSD-2-Clause; `text-origin.json` records the copied first-party proposal identities.

## Attempts and review

The preliminary 73-case command suite passed. Review then identified an oracle gap:
queued or partial requests could be discarded during cleanup after terminal
observation. Final owners explicitly require no partial frame and channel EOF
before accepting termination. The older empty-output witness receives the same
check. New controls exercise traffic after both closes and a broken parser that
publishes stdout before validating stderr. Neither a matching exit status nor
missing child terminal record substitutes for zero request evidence.

`preliminary.tar.gz` retains the preliminary inputs, artifacts, cases and logs.
Final builds also retain each case's generated text header separately. No failed
runtime attempt was observed in the preliminary run; it is superseded evidence,
not qualification of the subsequently added controls. Suite receipts bind all
implementation source bytes and check them again at completion.

## Scope and remaining work

Positive coverage includes help/version on stdout with empty stderr, usage on
stderr with empty stdout, read-right denial, complete one-byte short writes,
backend readback, explicit close and two generations/four reclaims. Malformed
second-record rights, duplicate role and stale generation reject with normal
bootstrap failure 110, no published authority/traffic and owner cleanup. Bad
output and omitted-close mutants require exact owner rejection; they do not claim
successful recovery from a bad client.

RL01–12 is not complete. Zero/fatal/exhausted writes, ambiguous delivery, close
failures, remaining carrier rejection cases and exact denied-admission outcomes
need separate witnesses. Composing output roles with startup/child launch, affected
owner review, immutable consumer handoff and independently rebuilt userland tests
remain open. UL-067 needs separate child diagnostic/admission authority. Neither
story is marked accepted, and full filesystem/package release readiness is not
established.

Reproduce with the full `--command-runner` invocation in NATIVE-COMMAND-IO using
SDK `/Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and lock
`/Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Use the same SDK/lock with `--inherited-launch` and `--connections` for regressions.

## Final qualification

All final checks pass: 76 command cases, nine inherited-launch cases, six
connections cases, 98 Python tests plus Zig/offline pin/workflow checks. The 13
stream cases include seven normal/expected-bootstrap-rejection witnesses and six
exact failure controls. The additional local post-close control also rejects as
specified. Rust and new C formatting, experience and diff checks pass. Stream
supervisors range from 3,160 to 4,968 bytes, below the existing 8,192-byte bound.
The backend adds exactly 768 bytes of sink arrays; this is not measured stack
high-water or a general native resource budget claim.

`qualification.json` records suite identities and verifies unchanged kernel/build
inputs against the preceding local-empty qualification. Final source hashes match
across all three suites. `attempt-2.json` records final command-suite start/end;
other receipt modification times are explicitly filesystem observations. Existing
per-case timestamps remain missing, so this is not full draft testing conformance.
`final-artifacts.tar.gz` retains source snapshots, case-specific generated headers,
compiled/native envelope artifacts and logs. ISO files, duplicate installed boot
copies and kernel.elf are omitted; ISO hashes and build commands remain in receipts.
Owner review and consumer adoption are still separate open gates.
