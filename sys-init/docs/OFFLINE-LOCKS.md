# Offline standards locks

This is the local reference for `docs/standards.lock`, `docs/experience.lock`
and `docs/distribution.lock`, consumed by their corresponding `docs/check-*.py`
wrappers. The wrappers and immutable released documents remain authoritative;
this reference does not standardize a new shared format or adopt the RC1 draft.

| Lock / wrapper suffix | Family | Vendored parent below docs |
| --- | --- | --- |
| standards | foundations | vendor/aether-foundations |
| experience | experience | vendor/aether-experience |
| distribution | distribution | vendor/aether-distribution |

Each lock contains exactly these five unique fields. Field order is immaterial.

| Field | Required value |
| --- | --- |
| format | `aether-<family>-pin-v1`, using the family above |
| version | `v` followed by three decimal digit groups separated by periods, such as `v0.1.0`; leading zeroes are accepted |
| source_project | Exactly `Aether-standards` |
| source_release | Exactly `<family>/<version>` |
| manifest_sha256 | Exactly 64 lowercase hexadecimal characters; SHA-256 of raw SHA256SUMS bytes |

The source fields are checked metadata, not network locations. The wrapper finds
its resolved script directory, reads its adjacent lock, and selects the version
under the fixed vendored parent. It never resolves source_project as a sibling
checkout or fetches source_release. Changing metadata cannot publish a candidate.
Existing release pins must stay fixed until an explicit release adoption.

Lock parsing reads at most 1 MiB of bytes, decodes ASCII and uses
`splitlines()`, splitting each row at the first `=`. Non-ASCII bytes reject. There is no whitespace
trimming, comment syntax or blank-line allowance. A final newline is optional;
LF and CRLF are accepted. Extra `=` characters remain in a value and fail its
field validation. Duplicate, missing or unknown fields reject. A UTF-8 BOM is
not stripped. These current parser details are not promises of a general text
configuration language; use plain ASCII and the committed lock layout.

## Manifest and execution order

After lock validation, the wrapper rejects symlinks in the selected release root
and its parents through the script directory, then enumerates the release tree
and rejects symlink entries. It reads SHA256SUMS, compares its raw SHA-256 with
the lock, and only then decodes and examines its rows.

Each manifest row is lowercase SHA-256, two spaces, and a name containing only
ASCII letters, digits, underscore, period, slash or hyphen. Names must be relative,
have no parent component, retain the same spelling through pathlib normalization,
be unique, and not equal SHA256SUMS. Every listed file digest must match. The
set of discovered files other than SHA256SUMS must exactly match the nonempty
listed set, including `conformance/check.py`. Empty directories are not listed.
A malformed row, missing file, changed payload, extra file, missing checker or
pin mismatch prevents the child invocation.

The child runs from a private temporary release copy made from captured bytes
whose digests match the verified manifest. Captured payloads have a combined
64 MiB limit. Original and staged trees are checked around execution; the staged
tree is removed on normal/error unwinding. The command is the running interpreter,
`-I -S -B`, then the staged `conformance/check.py`. Python environment options and
import paths, user site and automatic site initialization are excluded; assertions
are enabled and bytecode writes disabled for all three families. Non-Python caller
environment and working directory are inherited. This is not a filesystem/network
sandbox. The interpreter and standard library remain trusted host dependencies.


Arguments to these wrappers are ignored, including `--help` and `--version`;
they still perform verification and invoke the reference checker.

Reference stdout/stderr are captured separately as raw bytes and replayed after
capture/cleanup. Successful bytes are preserved; output is no longer live.
There is no wrapper JSON result. Normal completion exits zero. Caught ValueError,
OSError and KeyError failures exit 1 with a string diagnostic on stderr. A child
nonzero exit raises an uncaught CalledProcessError (normally traceback and exit 1);
the child's exact nonzero status is not forwarded. Native behavior and renderer
conformance do not follow from these development checks.

## Lifetime and remaining work

The lock is read once, the manifest bytes are captured for both hashing and
parsing, and payload bytes are read for hashing. The child opens the verified staged copy instead of the original source. Immediately before invocation and after a successful child, wrappers repeat
release path/type and complete file membership checks, compare the lock and
manifest bytes, and rehash every listed payload. Persistent changes reject.
The post-check runs after the child has already forwarded its output, so a child
success line followed by wrapper exit 1 is a failure. Failed children retain
the existing CalledProcessError path. There is no atomic verify-and-execute step.
A matching digest establishes bytes only, not signer authority, freshness or
independent review. Python imports and interpreter dependencies are not a sealed
execution closure.

Each lock, manifest and payload is limited to 1 MiB. Release traversal allows
at most 2,000 entries including directories. Inputs must be ordinary files;
symlink components at/below the resolved script directory reject. Opens use
nonblocking mode and no-follow where available. Descriptor type/device/inode
must match the preceding path check; size and mtime are compared after reading.
Descriptors close on failure. Reads allow at most one extra byte to detect growth.

The reference child has a 30-second deadline through pipe draining and exit,
and a combined 4 MiB stdout/stderr cap. Accepted raw prefixes are replayed on
success or failure. Timeout raises TimeoutExpired; overflow raises ValueError.
Capture failure or Python interruption kills the owned process group and reaps
the direct child before staged-tree cleanup. Cross-stream ordering is unspecified.
Standalone wrappers do not bound staging/I/O time or blocked output replay. The aggregate supplies its separate gate time/output limits;
it does not make filesystem operations atomic. Lock symlinks and special-file inputs reject before reads. Do not interpret existing
symlink checks as protection against hostile concurrent directory replacement.

BG-056 retains filesystem I/O deadlines, consistent identity through execution
and interpreter/environment closure. These are known
implementation gaps, not approved exceptions. Independent technical/reader review
and release authorization remain open. No new release pin is adopted here.

[Existing wrapper tests](../tests/test_harness_standard_wrappers.py) cover synthetic
Experience invalid inputs and Experience/Distribution assertion-mode behavior.
[Lock reference tests](../tests/test_harness_offline_locks.py) exercise all three
wrappers with synthetic private trees, including accepted line endings/order,
field failures and invocation ordering. They mock child execution; real released
reference checks are separately run by `python3 scripts/check-all.py`.
[Input controls](../tests/test_harness_standard_inputs.py) test read/traversal
limits, special files and controlled replacement/growth with all three wrappers.

Decision 0121 adds [identity controls](../tests/test_harness_standard_identity.py)
for persistent lock/manifest/payload, extra/missing-file and symlink changes
before invocation and during a synthetic child. Real-child controls demonstrate
stdout forwarding followed by post-check exit 1. A change restored between
comparisons can still escape detection; interpreter closure and hostile same-user mutation remain outside these checks.
Private staging does not make the input source tree an atomic snapshot.

Decision 0122 [private-execution tests](../tests/test_harness_standard_private.py)
verify that original-source replacement at dispatch does not change the executed
copy, Python isolation flags take effect, and child failures clean the temporary
tree. The total-budget control lowers the constant for its fixture. Abrupt process
termination can leave temporary files; the child deadline does not bound abrupt termination or filesystem operations.

Decision 0123 [capture tests](../tests/test_harness_standard_capture.py) verify
raw-stream/nonzero compatibility, real timeout/overflow/closed-pipe cleanup and
staged-tree removal. The tests use smaller budgets for timely controls. Escaped
descendants, SIGKILL, signals outside active capture and blocked output sinks remain outside the
capture guarantee; owned-group cleanup is not complete process containment.

Decision 0124 handles SIGTERM during main-thread child capture as interruption.
The owned group is killed and direct child reaped; Python unwinding removes the
staged tree. Secondary SIGTERM is ignored during capture cleanup; the previous
handler is restored before output replay and temporary-directory unwinding.
Background-thread calls do not install handlers. The CLI reports
`reference check interrupted` on stderr and exits 130 for KeyboardInterrupt,
including handled SIGTERM and ordinary SIGINT. Startup/Popen, staging, postchecks,
repeated signals after restoration and blocked output remain outside this scope.
[Termination tests](../tests/test_harness_standard_termination.py) exercise real
SIGTERM, custom-handler restoration and background-thread calls.
