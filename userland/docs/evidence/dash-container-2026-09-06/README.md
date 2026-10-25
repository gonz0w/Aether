# UL-077 — remote lifecycle prototype and witnesses

PLAN.md defines the first slice. The module is deliberately not integrated into
build.py/test.py yet; their previously recorded remote cleanup gap still applies.

Eleven deterministic protocol cases cover success, guest exit 7, attach timeout,
foreign ownership, service loss, failed removal, create ambiguity with absence,
name collision, survival after successful removal response, reserved client exit,
and create ambiguity with an observed owned container. The last case cleans up
what it observes but stays unresolved because late creation is not ruled out.
Models pass on Python 3.10.21 and 3.14.7. The initial ten-case runs and later expanded
runs are retained; these are model results, not remote service-failure witnesses.

Three real tests used the existing Podman 6.1.0 client/VM and already pinned arm64
image. No new image, machine, service or connection was installed. Commands were
`/bin/sh -c` with `printf "guest ok\n"`, `exit 7`, and `sleep 30`. Success preserves
exact output; nonzero preserves exit 7. The 0.5-second attach timeout terminates the
local client. A subsequent inspection proves that the remote container was still
running; it is then forcibly removed by exact inspected ID. Additional independent
exists queries return 1 for both name and ID, with complete local receipts. All
three attempt containers were observed absent. See live.json, raw logs/receipts and
timeout-witness.json. Removal response alone was not the oracle.

Runtime/source/tool/connection identities are in live.json and sources.json. No
private key bytes were read or copied into this packet. Explicit URL/identity paths
are retained so the remote connection boundary is identifiable. The descriptor pins
the local client bytes before execution; this is not daemon/SSH-server provenance
or full shared-library closure. No new remote ownership standard is defined here.

Commands from repository root:

```
python3 -B experiments/dash-reference/test-container-process.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/dash-reference/test-container-process.py
python3 -B build/dash-container-review/live.py
python3 -B build/dash-container-review/verify.py
python3 -B docs/quality/check.py
```

Live scripts are retained for evidence, not automatic replay: their explicit local
connection belongs to this run and must be reviewed/pinned before a future run.
The first capability probe used unsupported `podman version --client`; local help
resolved this to `podman --version` (6.1.0). The first sandboxed image inspection
failed with connection operation-not-permitted. The authorized escalation reached
the existing image; these setup failures are not guest semantic failures. No remote
service was restarted to resolve them.

Independent review is pending. True service-loss/late-create witnesses, integration
with writable target-generator mounts and read-only test mounts, unchanged guest
semantics, and full dash regressions remain UL-077 work. Owner SIGKILL, hostile
session escape, competing resource mutation and daemon compromise are outside this
prototype. Prior UL-075/076 reviews remain separate; no user approval is inferred
for this new code. No release pins or sibling files changed.
