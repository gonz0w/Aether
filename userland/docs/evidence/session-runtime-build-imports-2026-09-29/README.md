# UL-007 pinned bundle support-module isolation

The prior candidate builder imported process/components by ordinary module name.
A Python caller that had already imported those names could substitute cached
modules, despite the selected bundle's complete source hashes. The reproduced
before case supplies a cached validator that admits a missing memory receipt;
both parent/helper links succeed with musl fallback and different unqualified ELFs.
This is a developer build-selection defect, not a native authority bypass. No
altered ELF was executed. Prior passing native results and original seals remain.

The corrected builder executes the two already verified support files into local
module objects. It never changes sys.path or installs/replaces sys.modules entries.
This is a direct dependency selection, not a module sandbox or general plugin
loader. Trusted build/support code remains code, consumed only after externally
selected seal verification. Concurrent hostile interpreter/source mutation and
arbitrary recipe safety are not newly qualified.

Tests reproduce the old defect, reject the omitted component under cached fake
validator/runner names before linking, and rebuild a valid bundle while those names
are poisoned. Two differently sealed validator copies in one populated interpreter
each execute their own two validations and reproduce the same parent/helper bytes.
These are five host build/import cases, with process cleanup receipts retained.
The maintained runtime.c, application.c, component validator, native inputs and
owned process helper are unchanged. No new native execution is needed for the
same whole ELF bytes; the earlier49 native runs retain their exact scope.

Corrected candidate manifest SHA256: `b634326de61e1c3e450d8fae6aaf210915daed7fa47e9460dd1f0448de33307c`.

See review.md, before-results.json, after-results.json, reject-after-results.json
and pair-results.json. The corrected candidate source/dependencies are delivered
as candidate.tar.gz after final integrity/quality gates. The earlier candidate and
all extraction evidence remain immutable. Independent technical/reader review and
SSDK promotion remain pending; this fix supplies no approval or release claim.

Aether's latest SI-07 v2 protocol review clears its design assessment. The next
larger local work is the complete opt-in bootstrap/transport and rebuilt runner/
bytecount handoff, with the affected UL-063 source-review gate before UL-058 behavior
changes. Kernel owner hooks, native qualification and sys-init policy remain scoped
separately. This packet does not claim that sustained runtime has been implemented.

Final syntax, unchanged native C/helper identities, prior complete evidence seal,
quality and whitespace checks pass. [Corrected candidate](candidate.tar.gz) and
candidate-SHA256SUMS retain the standalone build inputs. Every private build
member was archive-readback verified before compaction; final-checks.json records
paths/digests and the remaining review gate. Native tests were not rerun because
all valid rebuilt whole parent/helper ELFs match the existing tested bytes.
Compaction reclaimed29011968 allocated bytes.
