# Experimental host descriptors and preparation API

This is the local reference for `prototypes/host_runtime/descriptors.py`, read
with `runtime.py` and `runtime_model/model.py`. It describes the implemented
`host-posix-experiment-v1` subset of pinned
[Distribution SV-01–05](vendor/aether-distribution/v0.1.0/SERVICES.md).
It does not define a production service format, native ABI, installation hook or
shared standard revision. BSD-2-Clause applies to this original documentation.

## Data and fields

`parse(raw)` accepts **bytes**, length 1–65,536 inclusive, decoded as UTF-8 JSON.
The top level must be an object containing exactly the thirteen fields below.
All fields are required: there is no omitted-field default, merging, variable
interpolation, shell expansion or comment syntax. Duplicate object keys reject
at every nesting level. Unknown keys reject at the top level and in `restart`;
`environment` and `requires` deliberately have variable names as keys. JSON
NaN/Infinity constants reject. Invalid encoding, malformed/deep JSON and invalid
values reject; valid JSON whitespace is allowed but affects the content pin.

An *identifier* here is 1–64 ASCII letters/digits/`._-`, starting alphanumeric.
Preparation additionally narrows **service IDs** to `[a-z][a-z0-9_-]{0,31}` through
the model. Package IDs retain the wider grammar; they are descriptive data, not
package authentication or an authority grant. Provider references must resolve
to actual prepared service IDs.

| Field | Required type and accepted values | Meaning and later validation |
| --- | --- | --- |
| `schema` | String, exactly `aether-service-experiment-v1` | No alternate version negotiation |
| `id` | Identifier | Unique in the prepared graph; narrowed model grammar above |
| `package` | Identifier | Syntactically checked only; not retained as a package authority token in `Service`/`Command` |
| `executable_sha256` | Exactly 64 lowercase hexadecimal characters | Expected bytes of `argv[0]`; checked against its file during preparation, activation and launch |
| `target` | Exactly `host-posix-experiment-v1` | Other targets reject; no native fallback |
| `argv` | Array of 1–16 strings | Each string at most 4096 UTF-8 bytes, no NUL; first string nonempty. Empty later arguments are allowed. Preparation requires the first argument to name an absolute executable file with the expected digest |
| `environment` | Object of at most 16 entries | Keys match `[A-Za-z_][A-Za-z0-9_]*`; values are strings, no NUL, at most 4096 UTF-8 bytes. Empty values allowed. No separate key-length bound beyond the total document bound. Preparation rejects reserved `AETHER_READY_FD` |
| `kind` | `long-running` or `oneshot` | Maps to model `daemon` or `oneshot` |
| `requires` | Object of at most 64 identifier keys | Values are `started`, `notified-ready` or `completed`; preparation verifies provider existence and compatible evidence |
| `after` | Array of at most 64 unique identifiers | Ordering references must exist; combined ordering/dependency graph must be acyclic |
| `readiness` | For long-running: `started` or `notified-ready`; for oneshot: `completed` | Chooses the model milestone; notified readiness uses the existing launch pipe protocol |
| `restart` | Object containing exactly `mode`, `retries`, `delay_ms` | See below |
| `authority_requests` | Empty array only | No authority broker exists in this adapter; requests are rejected, not silently granted |

`restart.mode` is `never` or `on-failure`. `retries` is a JSON integer from 0
through 2 inclusive; booleans and floating-point equivalents reject. `delay_ms`
is an integer from 1 through 60,000 inclusive, in milliseconds, also excluding
booleans. `never` requires zero retries; oneshot requires `never`. Long-running
`on-failure` with zero retries is accepted. The mode itself is not carried into
the model: the retry count/delay encode this narrower behavior.

These limits intentionally differ from the shared reference's 64-service graph,
16 retries and zero-delay allowance. Each prepared graph has 1–8 descriptors
and at most **16 total edges**, counting entries in both `requires` and `after`.
A provider appearing in both contributes two edges. Self-dependency, self-ordering,
missing references, combined cycles and incompatible milestones reject.
A oneshot provider supplies only `completed`; a daemon supplies `started`, or
`notified-ready` when its own milestone supports that evidence.

Descriptor conversion fixes startup, stop and cleanup budgets at **1000 ms each**.
These are not configurable fields. They differ from direct `Service` constructor
defaults and from the separate `HostRuntime.start/stop` request budget, which
defaults to 3000 ms. Do not infer one budget from another.

## API and ownership

| Call | Result and checks | Effects and ownership |
| --- | --- | --- |
| `parse(raw: bytes)` | Returns `(Service, Command)` with tuple-valued arguments/environment/edges | No file access, process launch or complete-graph validation. Does not check executable existence, absolute path or reserved readiness environment yet |
| `Prepared(paths)` | Requires list/tuple of 1–8 file paths; resolves paths strictly, reads up to 65,537 bytes, parses documents, checks unique IDs and executable files, validates complete model graph | Pins the exact raw descriptor bytes with SHA-256 and stores resolved paths. Holds no open descriptor-file handles and launches nothing |
| `prepared.activate(cwd=...)` | Reopens resolved paths and rejects changed content; constructs a new `HostRuntime`, revalidating model/commands and executable bytes | Resolves and requires a directory for `cwd`. Returns an independent runtime with a new host epoch; still launches nothing. Does not consume the preparation object; repeated activation is possible |
| `runtime.start(names, budget=3000)` | Requests model start and dispatches resulting effects | This is where actual child launches can occur. Caller must pump observations or use `until` and must own cleanup |
| `runtime.close()` | Permanently closes admission and attempts emergency cleanup of tracked children/readiness resources | Use in `finally`. Failures raise and remain available for retry; this is not an orderly-stop success record or containment of arbitrary descendants |

The caller must retain the prepared object and resulting runtime and use this
single-threaded experiment without concurrent mutation. Public Python attributes
are not tamper-proof handles; callers must not mutate `inputs`, `services` or
`commands` to bypass the intended workflow. Preparation does not lock the files,
bind a file descriptor across activation or grant one-shot launch authority.

Preparation records **resolved** paths, so an original symlink alias is followed
rather than pinned as an alias. It does not enforce file owner/mode, reject all
symlinks or restrict files to a package root. Supply trusted regular files in an
owned fixture directory. Reads are bounded in bytes, not elapsed time; this is
not a general parser service for devices/FIFOs or a hostile filesystem.
Concurrent rename/write/exec races and script interpreter/module provenance are
outside the content-hash guarantee. File I/O and pathname errors can propagate
as Python exceptions rather than `Rejected`.

## Environment, execution and changes

The child environment starts with `PATH=/usr/bin:/bin` and `LC_ALL=C`, then applies
the descriptor entries. Explicit descriptor `PATH` or `LC_ALL` therefore wins.
The ambient shell environment is not copied wholesale. For notified readiness,
the adapter adds its own `AETHER_READY_FD`; descriptors cannot supply that name.
The child inherits only the intended readiness writer among adapter-managed
extra descriptors. Standard input, output and error use the null device.

`argv` is passed as structured process arguments. Shell-shaped text remains
literal unless the selected executable is itself an interpreter that evaluates
it. Pinning `/bin/sh`, Python or another interpreter does not authenticate its
scripts/imports. A command runs with the invoking user's authority; this adapter
is not privilege separation or a sandbox.

There is no watcher, reload signal, overlay precedence, enablement store or package
selection transaction. Any raw-byte edit after preparation, including whitespace
or equivalent JSON key reordering, causes activation to reject. Create a new
`Prepared` object to select new descriptor content. Already-created runtimes use
their in-memory service/command values; they do not reread descriptor files before
each launch. They do recheck executable bytes at launch. A mismatch at that point
becomes the existing `launch_failed` model event, not successful execution.

## Errors and evidence

Semantic rejection uses `prototypes.runtime_model.model.Rejected`; it has no
stable numeric API error-code scheme. Malformed JSON and duplicate-key decoding
failures can be reported as `invalid descriptor JSON`. Do not promise one message
for every underlying parse error. Filesystem exceptions, incompatible Python
argument types and infrastructure errors can escape separately. Preparation
failure returns no usable object; activation failure launches no child. Emergency
cleanup can fail independently and must not be reported as successful shutdown.

Existing tests in `tests/test_host_descriptors.py` exercise actual launch,
stale content, nested duplicate/unknown/nonfinite input, unsupported profiles,
graph rejection and inert shell-shaped arguments. Decision 0106 adds focused
contract probes for parse-versus-prepare validation, exact limits, byte-stale
selection, environment precedence and no-launch preparation/activation. This
maps named behavior, not exhaustive input fuzzing or all-platform conformance.

The runnable [owned host example](examples/host-descriptor.py) constructs one
oneshot descriptor in a temporary directory, hashes the running Python executable,
prepares/activates it and explicitly starts it. It has a five-second observation
limit and `finally` cleanup. Run from the checkout with Python on a supported POSIX
host:

```sh
python3 docs/examples/host-descriptor.py
```

This launches a real trusted child and writes a temporary descriptor; it does not
install a service. Expected stdout is `host descriptor example: pass`, exit zero.
No root privileges or network access are required. The example uses runtime
checks rather than Python assertions for its success condition.

Missing publication work remains explicit: installed configuration/API manuals,
independent technical and reader review, target lookup, complete hostile-input
and filesystem policy, and production service-format decisions. New shared rules
belong in Aether-standards; exact local behavior and this evidence stay here.
