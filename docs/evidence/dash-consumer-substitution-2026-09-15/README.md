# Unchanged consumer command substitution — 2026-09-15

This selection runs the unchanged consumer substitution.sh and helper on Aether.
The helper receives `/inputs/helper`, `argv`, `a b`, and `*`, with WITNESS=value.
Its eight-byte `argv ok` plus newline passes through an inherited pipe writer.
Dash captures and strips the newline, checks the result, and writes exactly
`substitution ok` plus newline. Helper0/parent0/backend17 repeat twice with six
reclaims. This is bounded producer evidence, not independent SDK acceptance or
an assembled R1 image.

## Review and boundaries

The [shell contract](../../NATIVE-SHELL-STARTUP.md#unchanged-consumer-substitution--2026-09-15)
records the preimplementation requirement, forbidden outcomes, owner, standards
and test selection. O-02–04, I-01/05/06, E-01–06 and SE-01–05 apply. Reuse the
existing pipe/exec bootstrap and unchanged helper: a new service, namespace or
argument transport is unnecessary. Existing argument limits fit this workload.
Pipe accounting now uses the selected expected byte sequence's length, replacing
the five-byte assumption at those checks without changing pipe capacity.

Native denied-exec rollback/retry, authenticated caller identity, explicit image
grants, frozen argument/table validation, CLOEXEC filtering, EOF, wait collection
and cleanup remain required. The replacement invokes the pinned consumer helper
only after validated startup/table/grant/mask restoration. No new dependency,
unsafe boundary, kernel operation, resource limit, sibling edit or released pin
change. Userland retains independent SDK and consumer intake ownership.

The native adapter's environment verifier now recognizes the exact shared
signal/substitution selection while still requiring PWD=/work, WITNESS=value,
LC_ALL=C and PATH=/nonexistent. Upstream scripts/helper are unchanged. Existing
machine markers and upstream output are preserved without presentation changes.

## Qualification

`focus-3.log` records the positive case and both semantic controls passing. The
wrong-argument control changes the staged replacement's `a b` argument after
validation. The skip control omits the actual helper call after startup. Both
produce no expected pipe bytes; the owner rejects premature EOF with result2175
and zero reclaims before observing a child terminal. These controls do not claim
an observed helper exit status.

`host.log` records 104 Python tests and required Zig checks passing on the final
runtime sources. `checks.json` records Rust/C formatting, the resolved formatter
hash, workflow, standards, whitespace and four simplicity input hashes. Full
connections qualification passes: connections.json and connections-results.json
record 358 cases in 1107.496005 seconds, below the 1800-second review ceiling, on
268 unchanged inputs. connections-traces.json verifies exact lifecycle traces;
final-checks.json records the final documentation checks.

`attempt-3-sources.tar.gz` and `final-sources.json` preserve final runtime/support
inputs. Earlier attempts retain their own exact source archives. Full reports
record SDK/tool identities; replay requires those external pinned prerequisites.
The preserved selector/driver scripts record focused/full invocation mechanics.

```sh
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/check_workflow.py
python3 docs/check-standards.py
```

The existing AT-CONNECTIONS workflow group includes the three new selections.
Final review/support inputs are preserved separately in review-inputs.tar.gz.

## Retained attempts

Two formatter lookup attempts failed without changing files; the formatter was
then located beside the pinned LLVM21 tools. Both diagnostic logs remain.
Attempt1 stopped before native execution because the existing literal environment
check recognized only the signal macro. The exact conditional verifier was updated.
Attempt2 passed the positive native case but expected owner2176 for wrong arguments;
actual pipe EOF rejection2175 occurs before helper termination. Attempt3 corrects
that ordering oracle and passes all three cases. Logs, source snapshots, commands
and generated artifacts are retained, not replaced with the successful result.

focused-artifacts.json records verified archives of all three generated roots;
duplicate removal follows verification against both archived members and originals.
Full artifacts and cleanup are retained separately. Prior sealed evidence remains
unchanged. Compatibility details belong in compatibility.json and the final receipt.

## Remaining work

Review the multi-stage pipeline workload against current owner and worker bounds,
then qualify unchanged pipeline.sh and early-reader.sh. Existing two-process pipe
experiments do not establish those exact consumer outcomes. Matching command-runner
coverage and independent SDK/userland acceptance remain before the next full
handoff. Recovery gaps, persistent filesystem/OpenZFS, package execution and
sys-init R1 assembly remain separate work.

Final compatibility: 674 of 685 prior ELF/raw images are byte-identical. Nine pipe
owners and the two small replacement writers changed and pass full regressions.
The writers share final cleanup with the new consumer selection. All changed
owners remain within four pages; the new positive owner is 14,152 bytes. Exact
before/after digests and sizes are in compatibility.json.

Final preservation: all 6,344 full-run artifacts were verified against
archive members and original files before removing their generated directory.
Together with focused runs, 4,753,619,221 bytes of verified duplicate output were
removed. SHA256SUMS seals this packet after final checks.
