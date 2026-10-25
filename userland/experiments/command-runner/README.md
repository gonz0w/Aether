# Bytecount preparation and command-I/O review (UL-056)

The independently authored bytecount command passes ten real host-libc cases and
eleven injected libc-call controls. It also compiles to an x86-64 musl object with
unresolved public read/write/close imports, ready for a separate native startup/
transport adapter. No native command executable was linked or booted in this step.

The command counts bytes from stdin, formats an unsigned decimal count plus newline,
handles short writes, and closes input/output once each. It has no native traps,
bootstrap calls, hard-coded input/output, shell parsing or library formatting
requirement. Arithmetic overflow, overlong syscall results, zero-progress output,
read/write failures and close failures refuse success. Read/write EINTR retries
are host-tested; close EINTR is never retried or treated as success by this command.
That does not establish native signals or alter musl's own close/EINTR behavior.
EAGAIN is an operational failure, not an unbounded retry or replay policy.

Counting invocation: `bytecount --decimal`, with `LC_ALL=C`. --help and --version
use stdout and exit 0; invalid arguments/environment use stderr and exit 64.
Operational failure exits 1, matching the shared Experience new-command contract.
The decimal output is ASCII with one trailing newline, no styling. Diagnostics
contain no untrusted argument values. CR-01 supplies no stderr grant, so diagnostic
writes there can fail; exit status remains authoritative and no ambient grant is
invented. Closing stdout failure prevents successful completion. These exits are
command outcomes, separate from the proposed runner's 125/126/127 mappings.

```sh
python3 experiments/command-runner/check.py --sdk build/native-c-xhkdw6jv
```

Host cases cover six-byte/empty/binary input, missing/wrong/extra option,
missing/wrong locale, help and version. Injected controls force three-byte input
and one-byte output, read/write EINTR, read EIO/EAGAIN/overlong result, write
ENOSPC/zero/overlong result and close EIO/EINTR. They verify exact output where
successful, no write after read failure, bounded refusal, and one close per FD.
The controls test command logic with injected calls, not the native adapter.
The host build uses the host platform libc/SDK, not musl execution. Native object
preparation uses pinned Clang and the previously tested strict-musl include tree;
no usable native FD bootstrap or TLS image is implied by an object.

[Evidence](../../docs/evidence/bytecount-prepare-2026-09-05/README.md) retains exact
sources, tool identities, host commands/results and native object inspection.
All three standards checkers pass. No compatibility tier or shell readiness is
promoted. See [command integration review](../../docs/COMMAND-IO-REVIEW.md) for
producer readiness, candidate framing and remaining acceptance boundaries.

## Subsequent native integration

UL-057 completed [nine native command cases](NATIVE.md) using unchanged bytecount
source plus separate entry/adapter. The preparation above remains host/object
evidence; the public runner and full CR-01 remain open.

## Public CLI proposal (UL-059)

[Startup and result contract](../../docs/AETHER-RUN.md) now specifies the proposed
public interface and fourteen acceptance cases. It does not change this finite
runner, exit 29, producer pin or existing native evidence. Affected-owner review
and UL-063 source audit remain before implementation.

## Owned tooling (UL-063)

All three drivers now use [process.py](process.py) for recorded process-group
cleanup and explicit environments. Run `python3 -B experiments/command-runner/check-process.py`
for seven host ownership/environment controls. Native builds require the exact
local tools in host-tools.lock.json; no PATH fallback or automatic download occurs.
The verified private Rust wrapper handles nested producer builds without exposing
Rust library overrides to other tools. Existing native invocation and producer
pins remain unchanged. See [audit checkpoint](../../docs/quality/COMMAND-RUNNER-REVIEW.md)
for failed attempts, validation and remaining scope.

## C17 build checkpoint — 2026-09-06

Current userland host/object and five-client builds select C17; historical C11
receipts remain unchanged. Pinned producer C fixtures retain C11. All 21
host/control cases and nine native cases pass, with five client ELFs identical
to the C11 baseline. The native driver removes only unreachable scenario branches;
its nine-case inventory and smoke contracts are unchanged. See
[evidence](../../docs/evidence/command-c17-2026-09-06/summary.json).
Python readability and independent review remain UL-063 prerequisites.

## Python driver structure — 2026-09-06

The three build/test drivers use explicit main() entry points and can be imported
without starting work. prepare-native.py names the runner/channel source inputs;
native.py separates expected failure contexts and terminal sequences into pure
helpers. Python 3.10+ remains the declared profile. Existing command invocation,
receipt schemas and native markers are preserved. All 21 host/control, seven
process-control and nine native cases pass, with unchanged five-client ELF bytes:
[review evidence](../../docs/evidence/command-readability-2026-09-06/summary.json).
Independent review and UL-058/059 boundary/public-contract work remain open.

## Failed-bootstrap boundary — 2026-09-06

The adapter now allows one initialization attempt per connection and poisons
transport on failure. Repeated bootstrap after success rejects while preserving
live bindings. Twenty-two host scenarios with UBSan and two mutation controls
pass; all 21 existing host/control tests and nine native regressions pass.

```sh
python3 -B experiments/command-runner/check-bootstrap.py --sanitizer undefined --mutations
```

[Evidence](../../docs/evidence/command-bootstrap-2026-09-06/README.md) retains
13 failing original scenarios, the correction and all reruns. ASan empty-main
and initial adapter checks time out on this host; address instrumentation remains
incomplete. Native injected failure cases and remaining UL-058 groups are open.

## Transfer/reply host controls — 2026-09-06

```sh
python3 -B experiments/command-runner/check-bootstrap.py --suite transfer --sanitizer undefined --mutations
```

53 host scenarios and two mutation controls pass; the adapter source is unchanged.
Tests require exact bytes, bounded retries, preserved failed-read destinations and
zero transport after poison. All 24 bootstrap and 21 command checks remain passing.
[Evidence](../../docs/evidence/command-transfer-2026-09-06/README.md) retains the
initial mutant build failure and corrected semantic rejection. Native failure
injection and ASan support remain separate incomplete work.

## Pure public startup parser (UL-059)

`runner-parse.c` decodes the reviewed 224-byte AERUN001 carrier into owned,
fixed-size storage. `ar_select` revalidates that storage and returns an action;
only `AR_LAUNCH` publishes copied child arguments and `LC_ALL=C`. Other actions
leave output unchanged, and callers must not use that output to launch. The
helper performs no transport, command lookup, authority acquisition or printing.
Help/version actions do not mean output was delivered or an exit status selected.

Run the host UBSan cases, two semantic mutation controls and native object check:

```sh
python3 -B experiments/command-runner/check-parser.py --sdk build/native-c-xhkdw6jv
```

The provisioned SDK and Clang are checked against the existing libc receipt.
Each command has a 30-second owned-process deadline and explicit environment;
all outputs remain in a new `build/runner-parser-*` directory. Missing prerequisites
or failed cleanup reject the run. This is deterministic boundary coverage, not
extended fuzzing, native execution or public CLI acceptance. ASan availability
remains tracked in UL-062. See [the contract](../../docs/AETHER-RUN.md) and
[parser evidence](../../docs/evidence/runner-parser-2026-09-06/summary.json).

## Opt-in native startup (UL-059)

`native_runner_bootstrap` is available only with `NATIVE_RUNNER_STARTUP`. It
owns one initialization attempt, decodes the carrier privately, then validates
both bindings before publishing arguments. It shares rejection/poison state with
the ordinary entry. The finite runner uses `ar_select` to construct the launch
frame; no fixture-provided argument offset remains in this path.

```sh
python3 -B experiments/command-runner/check-bootstrap.py --suite startup --sanitizer undefined --mutations
python3 -B experiments/command-runner/native.py --aether ../aether --sdk build/native-c-xhkdw6jv --producer ../aether/docs/evidence/native-runner-combined-2026-09-06 --startup-controls
```

The native flag selects the separately pinned producer and adds three positive
startup cases and one fourth-argument corruption control to the nine baseline
cases. It combines with the earlier boundary flags. The independent observer
checks full child argc/argv/environment, then runs bytecount on its two supported
arguments; it is an experiment witness, not an extra-argument mode for bytecount.
The producer checks actual output and cleanup. The finite parent still exits29;
public help, result mapping and zero-admission/recovery are not implemented.
See [retained evidence](../../docs/evidence/runner-startup-2026-09-06/summary.json).

## Pure admission and collection results (UL-059)

`runner-result.c` decodes the existing 32-byte replies for this two-generation
experiment. Admission requires its exact generation receipt; collection requires
the caller's expected receipt. Error payloads must be zero and wire errno must be
in -1..-4095. Collection -11 means pending; the same admission error remains an
owner error. Success validates reserved fields and terminal kinds 1/2/3. Raw
uint32 detail is preserved, including values that cannot be a CLI exit status.

```sh
python3 -B experiments/command-runner/check-results.py --sdk build/native-c-xhkdw6jv
```

Only a non-invalid decoder action publishes output. Invalid output storage is
unchanged and must not be reused as a result. `ar_terminal_exit` is used after a
collected result: normal 0–255 and explicit completed cleanup preserve the child
status; other outcomes return1 while leaving raw facts intact. These pure helpers
perform no exchange, retry, receipt consumption, cleanup or authority validation.
The caller still owns those states and must treat ambiguous delivery as unknown.
The finite/native runner does not yet call the helpers. See
[result evidence](../../docs/evidence/runner-results-2026-09-06/summary.json).

## Opt-in collected-result mapping (UL-059)

`--mapped-results` selects the reviewed producer's startup and mapped-result
modes for 13 additional cases. The corresponding parent uses `ar_admission` and
`ar_collection`, retains raw terminal facts through cleanup, and calls
`ar_terminal_exit` after required EOF/close checks. It sends one admission and
repeats collection only after a validated pending reply; ambiguous/malformed
outcomes abort this bounded experiment without replay. No unattended recovery
or zero-admission public outcome is implemented.

```sh
python3 -B experiments/command-runner/native.py --aether ../aether --sdk build/native-c-xhkdw6jv --producer ../aether/docs/evidence/native-runner-combined-2026-09-06 --mapped-results
```

The flag alone runs nine baseline plus 13 mapped cases. With all earlier boundary
flags, the recorded suite has 47 cases. Link-only child wrappers produce normal
0/1/2/64/125/126/127/134/255 or an actual fault after bytecount output. Incorrect
kind/zero mappings must be rejected by the producer. The local close-error control
performs the real close before reporting EIO and checks raw facts at policy entry;
its parent1/broker970 outcome is deliberate rejection, not remote cleanup recovery.
The default pin and finite parent29 path remain unchanged. See
[mapped evidence](../../docs/evidence/runner-mapped-2026-09-06/summary.json).

## Mapped-path uncertainty host controls (UL-059)

```sh
python3 -B experiments/command-runner/check-mapped.py
```

This compiles actual runner.c/mapped-runner.h and real parser/result code with
scripted bootstrap, exchange and file-I/O seams. Each of 25 fresh processes checks
exact request bytes, call ordering, lost/malformed/rejected replies, pending limits,
raw facts and cleanup. Four private header mutants must reject at named oracles.
The 100,000th collection can complete successfully; 100,000 pending replies exhaust
the budget, and a 100,001st request is forbidden. Unknown/malformed replies permit
no later exchange/read/close/policy call in this bounded abort path.

The shim operates at the complete-exchange boundary. It does not model native
fragment delivery, real descriptor closure or recovery. Earlier adapter/native
witnesses remain separate. No production code was changed. See
[host evidence](../../docs/evidence/runner-uncertainty-2026-09-06/summary.json).

## Native mapped uncertainty (UL-059)

```sh
python3 -B experiments/command-runner/native.py --aether ../aether --sdk build/native-c-xhkdw6jv --producer ../aether/docs/evidence/native-runner-combined-2026-09-06 --mapped-uncertainty
```

The flag also selects mapped-result cases, adding six uncertainty controls to the
nine baseline and thirteen mapped cases. Combined with all earlier boundary flags,
the recorded suite has 53 cases. Parent wrappers validate a complete real success
reply before losing its final receive acknowledgement or corrupting metadata.
The real runner must return1 without later guarded calls. Wrapper exits101/102
prove admission/collection observations; a private retry mutation must exit109
before reaching the adapter. The owner deliberately rejects at970/reclaimed0.
These are bounded abort witnesses, not resource recovery or public local outcomes.
See [native uncertainty evidence](../../docs/evidence/runner-native-uncertainty-2026-09-06/summary.json).

UL-062 [extended parser checks](EXTENDED.md) provide a fixed host mutation workload,
failure retention/replay, local minimization, static analysis, observational RSS
metrics, forked concurrency, a host transport loop, pinned-ASan deadlock diagnosis
and explicit sanitizer selection; native acceptance remains separate.
