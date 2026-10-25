# UL-077 — revised transport fixture qualified

The user authorized starting the existing Podman VM. The first start reported
success, but subsequent separate command sessions found its endpoint unavailable
and machine status reported stopped. Both first test attempts failed before creation;
the improved recovery reporting correctly made no remote cleanup request. Those are
setup failures, not passing transport denials. No container was created by them.

Repeating startup, endpoint verification and both tests within one command session
succeeded. This is an observed execution-session requirement, not proof of the exact
cause of VM termination or a claim that the VM remains running after session exit.
No new machine, image pull, rootful switch, helper installation or sibling edit was
performed. machine-start*.log preserves the tool's optional setup suggestions; none
was executed. The initial info query's connection-refused error was reported through
the tool output; its redirected stdout contains a short client summary rather than JSON. The retry
retains raw info.

The current relay and recovery fixture both pass on Python 3.14.7 and 3.10.21.
For each successful run, creation and ownership inspection precede the relay cut.
Actual Podman attach and cleanup calls then fail with connection refusal. The original
receipt remains complete=false/cleanup=unresolved. Separate recovery through the
original connection verifies exact name/label/ID, removes only that container and
observes name and ID absent. Revised EOF handling and setup-failure reporting are
therefore exercised with the real endpoint on both tested runtimes.

Successful command sequence (repository root, one execution session):

```
podman machine start podman-machine-default
podman info --format json
python3 -B experiments/dash-reference/test-container-transport.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/dash-reference/test-container-transport.py
```

Startup and each subsequent stage must succeed before the next stage. Runs use the
existing immutable image and frozen client/connection described in their receipts.
No private-key bytes or SSH payloads are retained. verification.json checks the raw
receipts, confirmed creation, real nonzero post-cut client statuses, original rejection,
separate recovery, absence queries and matching current fixture hashes. It is a local
review of live receipts, not an additional later remote absence query.

The local quality gate passes. Independent review and true in-flight/lost-create-
response controls remain open; this is post-create connection loss, not creation
ambiguity or shared daemon failure. Earlier blocked records stay historical. No
production adapter/build/test changes, release-pin updates or native acceptance.

Raw Podman output whitespace is preserved through exact-file .gitattributes
exemptions. whitespace-review.json retains the initial check/hook failure.
