# 0007: Preserve unknown status when wait ownership is lost

Accepted 2026-09-05 for BG-028/BG-054's trusted, single-threaded adapter. Pinned
Foundations O-04, I-04 and E-06 apply through existing adoption. This is a local
wait-observation contract; native ABI, shared releases and control IPC are unchanged.

## Finding and behavior

Inspection of this host's Python subprocess implementation found that its poll
path substitutes return code zero when waitpid reports ECHILD. The
[implementation fingerprint](../evidence/host-wait-ownership-2026-09-05/python-wait-behavior.json)
identifies the exact local version. A test consuming exit 23 through a competing
raw waitpid before adapter polling demonstrated that this fallback could falsely
complete a one-shot successfully.

The adapter now observes uncached statuses directly with waitpid(pid, WNOHANG),
converts real wait status using os.waitstatus_to_exitcode, and stores that status
in the owned Popen object's returncode cache. Existing successful cached waits
remain usable. This uses POSIX child waiting and standard-library Python host
tooling; it does not introduce a target dependency or implementation-language choice.

ECHILD marks that Popen object as having lost wait ownership. Polling produces
one model `lost` observation and closes its readiness reader. Known-lost objects
never receive signals or successful reclamation from adapter dispatch. Retain
the object and model ownership as unresolved; do not recover authority from its
numeric PID. Emergency close attempts other children but reports cleanup failure
for the lost object, including on subsequent retries. No historical operation is
converted into success. The retained inventory is bounded by the existing graph.

The direct wait check replaces status synthesis, not the supervisor's ownership
architecture. The supported runtime is still single-threaded with exclusive wait
ownership and no competing wait/SIGCHLD handler. This is detection of observed
ownership loss, not enforcement against concurrent waiters, external mutation of
Popen objects, hostile PID races or a forged cached returncode. Do not treat the
public experiment objects as an authority boundary. General recovery remains open.

## Helper boundaries

A separate helper cannot collect another process's child status in the tested
host relationship. The owner remains responsible for waiting. In contrast,
readiness is explicitly delegated by descriptor possession: a main process can
pass the writer to a helper, wait for that helper itself, and have its generation
become ready. This confirms decision 0003's contract; it is not main-PID
authentication or an independently owned readiness service.

Three new tests use real children: stolen wait status becomes incomplete/unknown
without signalling the lost identity; a sibling helper gets ChildProcessError
while the original owner can still reap; and a delegated helper signals readiness
and is reaped by its parent before the main service is stopped. Only the stolen-
status test knows the actual already-consumed status; after its assertions, its
teardown sets the Popen cache from that real status to avoid a misleading Python
destructor warning. Production adapter code does not perform this repair.

## Evidence and remaining work

The [combined report](../evidence/host-wait-ownership-2026-09-05/positive/results.json)
passes all three standards checks, 34 model tests/three mutation controls, 38 host
tests and 10 harness tests on macOS. Restoring Popen.poll produces the expected
false-success assertion failure: [control](../evidence/host-wait-ownership-2026-09-05/negative.json)
and [log](../evidence/host-wait-ownership-2026-09-05/negative.log).

BG-028 retains measurements, stronger exclusive-wait enforcement and broader
helper containment; BG-033 retains native recovery; BG-054 retains cross-host/CI.
The parent-death containment gap from decision 0006 remains. This change does
not select a production process architecture or resolve those gates.

A concurrent native-build script change after the run is recorded in the [snapshot note](../evidence/host-wait-ownership-2026-09-05/snapshot-note.json). Host runtime/test hashes still match; the report is a historical snapshot, not evidence for later native edits.
