# UL-077 — dash guest lifecycle integration

PLAN.md records scope, standards and acceptance. test.py now uses the lifecycle
adapter for all guest cases; host helper compilation continues through UL-076.
It freezes the existing default SSH connection/client identity before compiling or
creating containers. No VM/configuration changes, image pulls or sibling edits.

The adapter gains a fixed read-only input mount, existing bounded scratch tmpfs and
existing guest environment. A model verifies exact construction and rejects the
repository root, entire build root and comma-injected path before client calls.
Eleven existing lifecycle protocol cases still pass. Both methods pass on Python
3.14.7 and 3.10.21; the initial pre-mount-test run is retained as well.

The full twelve guest cases pass on both interpreters. Independent comparison checks
all scripts, expected exits and stdout hashes against the original reference record;
dash and helper digests match too. All semantic negatives retain their expected
results. Traces are new, not claimed byte-identical. Actual argv, SDK/tool/build pins,
connection-selection logs and local/remote receipts remain in each retained run.
The command inventory now records actual attach argv, guest argv and receipt path;
aggregate evidence adds adapter/client identity. Existing stdout/trace paths remain.

A separate post-suite verifier queries both the exact name and ID of each of the
24 attempt containers: all 48 queries return absent with complete local execution.
verification.json and its raw receipts bind these observations. This establishes
only observed cleanup on the identified existing VM; live service loss, competing
mutation, late create and owner-SIGKILL remain outside this integration witness.

Commands (repository root):

```
python3 -B experiments/dash-reference/test-container-process.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/dash-reference/test-container-process.py
python3 -B experiments/dash-reference/test.py build/dash-reference-zx5wokn_
build/python-qualification/Python-3.10.21/python.exe -B experiments/dash-reference/test.py build/dash-reference-zx5wokn_
python3 -B build/dash-container-integration/verify.py
python3 -B docs/quality/check.py
```

No guest failure or skipped case occurred. Model results do not substitute for live
fault tests. The selected-descriptor paths contain no private-key contents. All
source identities are in sources.json; old evidence/census hashes remain historical.
UL-076's full guest-integration requirement now has evidence, but independent review
is still pending. UL-077 stays active for writable generated-tool lifecycle support,
affected full builds, review and the remote ambiguity work. No release pins changed.

The first staged whitespace check flagged raw QEMU trace spacing.
whitespace-review.json retains that output; .gitattributes exempts only the exact
affected immutable trace files. Original source checks remain enabled.
