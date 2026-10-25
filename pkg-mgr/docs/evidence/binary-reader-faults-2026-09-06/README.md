# Binary metadata reader review and candidate refresh — 2026-09-06

HR-02/HR-04: field, uname and record-version reader status must succeed before
comparison or target-record construction. The regression demonstrated export
returning success when the target_runtime reader printed the correct value then
failed. before-test.log and before-result.json retain that attempt under a
300-second process-group watchdog. before-binary.sh, before-binary-package.sh and
before-inputs.json identify its exact implementation and test inputs. This proves
false-success export, not observed acceptance of incompatible host binaries.

Runtime/dependency fields, imported host identity, uname and the first record line
are now captured with checked assignments before comparison/use. Successful record,
receipt and diagnostic formats remain unchanged; no new runtime dependency or
standard is introduced. Export host identity assignments were already checked;
new controls cover them alongside the corrected sites.

Oracle: each selected reader prints its genuine output then returns 73, with a
required marker. Five field controls (runtime, base dependency, OS, architecture,
compiler target) exercise export and import; two uname options and one version read
exercise import. All thirteen must reject without stdout or publication and leave
target file/hash/mode snapshots unchanged. Existing round trips, exact receipts,
incompatible identities and retained recovery remain positive/negative controls.
Wrappers delegate all other calls to the captured host tools. The initial scoped
lint found two unquoted literal uname assignments in the test; before-lint.log
retains those findings. Quoting the literals corrected them without suppressions.

Validation plan: scoped lint in the development checkout, then explicit public
candidate assembly and full sh tests/check.sh from its extracted tree under the
existing 600-second watchdog. This validates the same selected runtime/test bytes
while also qualifying the artifact. Host preflight and required manual/bytecount
checks also run from that extracted candidate. Preserve exact input manifests,
archive digest, individual outcomes, raw logs and post-test selected bytes/modes.
No previous-candidate test repetitions are transferred to this candidate.

This is local experimental host qualification, not independent review, a captured
clean builder, Linux/BSD support, physical full-storage/power-loss durability,
concurrency safety or publisher authentication. Captured setup, broader failure
qualification, independent content/build/reader review, a monitored security
contact and publication approval remain separate gates. No tag/sign/upload occurs.


## Candidate identity and workflows

The 187-file archive SHA-256 is
`9872d60f0077d132d60696c0a11ea038910bbb8512997d9ac0585e752d74e043`.
It is 1,024,000 bytes, retained at
`/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-release.7tdurxhw/pkg-mgr-0.1.0-candidate.tar`.
Repeated assembly and host-tar extraction match exact bytes/modes. The input and
output manifests plus the documentation edition receipt are retained. Six inputs
changed since the last qualified archive; none were added/removed. This includes
the earlier descriptor and final-preflight hash fixes as well as this reader fix.

Host preflight and required manual rendering/lookup/bytecount checks pass from
the extracted candidate. host-result.json and manuals/result.json identify tools
and inputs; raw/rendered outputs are retained. These workflows overlap the full
suite in independent private roots; timings are not comparative performance data.
No separately provisioned clean-builder result is claimed.


All sixteen fixtures, three pinned standards gates and whole-shell/scoped lint
pass. The thirteen new reader controls and preceding descriptor/preflight/intent
hash controls pass from this archive. Post-test verification confirms all 187
selected file bytes/modes, development assembly inputs, manifest and retained
archive are unchanged. suite-result.txt records the run and 600-second deadline.
This is one transaction-fixture run on this archive; prior repetitions are not
transferred. Qualification evidence is copied beside the retained archive.
