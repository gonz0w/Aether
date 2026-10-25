# Native adversarial signal frame tests

Preimplementation requirement: exercise rejection of forged real signal frames
through the existing native return operation. No kernel, ABI, quota, SDK, sibling
or released-pin changes. The fixture owns its writable copied payload; the
kernel retains all CPU/mapping authority. No pending signals are enabled.

The handler copies its actual 720-byte payload using its compiler-established
frame pointer. A small naked assembly helper switches user RSP to the candidate,
issues 0x1000f, and recovers the caller stack through R11 only if rejected. It
makes no privileged transition itself; it runs on the same user mappings. Each
bad-field attempt must return EINVAL and leave candidate bytes and signal mask
unchanged. Correct acceptance transfers to the saved continuation instead.

Simplicity: extend the existing startup fixture and full command harness. Do not
introduce a new kernel mutation flag or separate runner. The uncorrupted control
submits a valid copy, resumes the saved continuation early, and must fail the
missing-rejection-count oracle at terminal78/owner1501. This proves the fixture
distinguishes acceptance from rejection without treating a crash as success.

Select full command-runner and host suites, C format and harness syntax/workflow
checks. Kernel code is unchanged, so no new M4 selection. Retain all attempts and
freeze test sources during qualification. Native altered page-table permissions,
full-register/red-zone checks, pending delivery and independent consumer review
remain separate acceptance work.

## Results

All 231 command-runner target cases pass on frozen final sources. The new positive
passes twelve rejected returns in each of two generations and the owner confirms
four reclaims. The valid uncorrupted control resumes the saved continuation and
produces exact terminal78/owner1501. The full host suite passes, including 98
Python tests and existing Zig/workflow/offline standards checks. C format, Python
syntax and the simplicity snapshot checks pass. No kernel changes were needed.

The initial attempt completed six passing cases before interruption to strengthen
the alignment test. Its seventh case is incomplete, not failed or passed. The
initial-startup-client.c reconstruction matches the original receipt hash; the
final source snapshot and test.patch identify the final delta from the prior
qualified self-upcall packet. attempt-note.txt corrects the earlier mistaken
commentary that the interruption preceded target execution. All attempt artifacts
and logs are retained. No runtime failure occurred in this work.

The emitted handler prologue establishes RBP and the naked return helper has
exactly the intended stack-switch/trap/restore sequence; full ELF disassembly is
in the retained command artifacts. This is native producer evidence for the
listed rejections only, not pending signal support or independent dash acceptance.
The fixed frame buffers total 1456 bytes plus a counter. No new quota is introduced.

Reproduce with the existing complete command-runner invocation in
[NATIVE-SHELL-STARTUP](../../NATIVE-SHELL-STARTUP.md). collect.py retains and verifies
source and artifact archives from existing harness receipts; it is an evidence
collection helper, not another developer runner or status system. Kernel hashes
are separately compared to the preceding qualified source snapshot.
