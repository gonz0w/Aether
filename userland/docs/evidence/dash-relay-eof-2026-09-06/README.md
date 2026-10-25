# UL-077 — relay EOF correction

The original fixture closed both socket directions when one peer sent EOF. Two
real loopback controls reproduce data loss: a request half-close prevents its large
response from arriving, and a response half-close discards a late client request.
Both baseline tests fail. relay-before.py and baseline.log preserve that attempt.

The relay now tracks read EOF and write shutdown independently, drains queued data
before propagating a write shutdown and preserves the reverse direction. It closes
a pair only after both input directions end and both queues drain. Existing socket,
queue, lifetime and no-payload-log limits remain. This is test-fixture code only;
container-process.py, build.py and test.py are unchanged.

Both controls now pass on Python 3.14.7 and 3.10.21. Each receives exactly 294,912
response bytes including NULs; server request bytes also match. All fixture server
threads finish and relay processes are reaped. Raw process errors, runtime/source
identity, byte counts/digests and cleanup observations are in each retained result.
These controls do not exhaust all TCP errors, capacity limits or interrupted teardown.

Commands from repository root:

```
python3 -B experiments/dash-reference/test-transport-relay.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/dash-reference/test-transport-relay.py
python3 -B docs/quality/check.py
```

The first command was run once before the fix (both failures) and once afterward
(both passes). No VM, container or external network endpoint was used by these tests.
The existing VM still reported stopped at turn start; live outage/create-response
qualification is incomplete, not a passing skipped test. No startup was attempted.
Independent review remains pending. The earlier SSH outage witness identifies older
fixture bytes and does not qualify this revised relay. No release pin or sibling
changes, native claims or broad standards acceptance follow from this fix.
