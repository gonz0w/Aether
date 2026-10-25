# UL-077 — live create-response loss

The fixture now supports --create-response. During create, the test relay delays
opaque server-to-client bytes by 0.5 seconds per received chunk. A separate observer
uses the original connection to find the actual labelled container and inspect its
name/ID/label. Only after writing this witness does it request relay termination.
No payload decryption, fake Podman response or shared-service shutdown is used.

The actual create client fails without delivering an ID on stdout. The unchanged
adapter records create_attempted=true, create_confirmed=false, container_id=null,
complete=false and cleanup=unresolved. No guest start is issued. Recovery through
the original connection verifies the owned resource and removes precisely the
witnessed ID, then queries name and ID absent. It does not upgrade the original
receipt. Pending encrypted bytes at the cut and a real backend create witness are
retained. This is a real committed-create/lost-response schedule; it is not evidence
for every possible delayed future creation or daemon failure schedule.

The observer uses bounded direct-client queries in an enclosing process group owned
by the fixture, with a 16 MiB file limit. It creates no independent process groups.
The fixture checks that this observer group is gone before accepting the control.
Direct observer query records describe leader waits; they do not independently claim
descendant cleanup. The original adapter's local helper remains unchanged.

Initial create-response tests passed on Python 3.14.7 and 3.10.21, as did both existing
post-create outage runs and EOF regressions. A compatibility review then restored
the original default success marker and added an explicit observer-source hash and
process-group exit-race handling. test-before-marker-check.py preserves that earlier
fixture version. Both outage modes were rerun on both versions at final source bytes;
all four final runs pass. Eight real test containers across all attempts were separately
recovered with recorded name/ID absence. No failed/skipped attempt is counted as a pass.

Commands (repository root; startup and live runs kept in one execution session):

```
podman machine start podman-machine-default
python3 -B experiments/dash-reference/test-container-transport.py --create-response
build/python-qualification/Python-3.10.21/python.exe -B experiments/dash-reference/test-container-transport.py --create-response
python3 -B experiments/dash-reference/test-container-transport.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/dash-reference/test-container-transport.py
python3 -B experiments/dash-reference/test-transport-relay.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/dash-reference/test-transport-relay.py
python3 -B docs/quality/check.py
```

The existing VM was started under the user's authorization; no new machine/image,
rootful switch, helper installation or persistent monitor. Client/image/connection and
fixture identities are recorded; no private-key or SSH payload bytes are retained.
verification.json independently reviews raw client receipts and witness/recovery
identities. It is not an additional post-session remote query. Source/run copies
and hashes preserve evidence. No runtime adapter, release pin or sibling changed.

The planned scoped UL-077 implementation/qualification is ready for independent
technical review. The consolidated handoff is docs/quality/DASH-REVIEW.md. UL-075–077
remain active until that review is supplied. Broader source migration, arbitrary
transport schedules, hostile daemon/competing mutation, owner SIGKILL and whole-suite
wall-clock guarantees are not closed by this result. Earlier missing-live-test records
are historical; no whole-system or native shell readiness claim follows.
