# UL-077 — real post-create transport loss

PLAN.md records scope and intended controls. The new test-only relay forwards
opaque SSH bytes through a temporary loopback listener. The test creates and inspects
one container through that fixed connection, stops only the relay, and calls the
unchanged lifecycle adapter's real Podman client. No fake client result is supplied.
No private key or SSH payload bytes are read into evidence. The shared VM/service
is not intentionally interrupted by this test.

Python 3.14.7 passes: creation was confirmed before relay termination, actual attach
and cleanup queries returned connection-refused errors, and the original container
receipt remains complete=false/cleanup=unresolved. A separate connection to the
original endpoint verified name/label/ID, removed only the owned container, then
verified both name and ID absent. Recovery is a separate record; it does not rewrite
the original unresolved outcome. Relay process termination is recorded.

Python 3.10.21 qualification is INCOMPLETE. Its attempt failed before any create
request: the original endpoint was unavailable. The recovery attempt also failed
because it tried to inspect through that unavailable endpoint. Both failures and
the original create_attempted=false receipt are retained. No container ID was
obtained and no create request was sent by this attempt. This is not a passing
transport fault control. machine-status.json subsequently reports Running=false;
this task did not start/stop/restart the VM. The reason for the VM state change is
not established here. The initial sandboxed machine-status query also hit the local
VM lockfile permission boundary; authorized read-only status collection succeeded.

Commands from repository root:

```
python3 -B experiments/dash-reference/test-container-transport.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/dash-reference/test-container-transport.py
/opt/homebrew/bin/podman machine list --format json
python3 -B docs/quality/check.py
```

The fixture has a 60-second relay lifetime, eight-pair ceiling, 1 MiB pending buffers
and 64 KiB chunks. Parent startup and termination waits are bounded. These are code
limits, not exhaustively fault-tested relay guarantees. The successful live run
exercises this particular SSH exchange; no general-purpose TCP proxy claim is made.
The fixture and its source hashes are retained, with all client/relay/recovery logs.

Remaining: qualify the final fixture on Python 3.10.21 when the existing VM is
available, improve recovery reporting when setup fails before creation, test a true
in-flight/lost create response, and obtain independent technical review. The current
control demonstrates post-create connection unavailability, not daemon shutdown or
create-response ambiguity. No maintained adapter/build/test behavior, release pins
or sibling repositories changed. UL-077 remains active; local quality checks do not
close missing live qualification or review.

Follow-up in this change: recovery reporting now skips remote calls when no create
request was sent and retains recovery errors instead of masking the original failure.
Three offline controls pass on Python 3.10.21/3.14.7 for no-create, unreachable and
absent cases. The successful earlier live execution is retained as test-executed.py
in the transport evidence packet; final fixture live qualification remains pending
until the existing VM is available. No runtime adapter behavior changed.
