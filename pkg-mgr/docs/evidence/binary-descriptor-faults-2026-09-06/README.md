# Binary descriptor hash failure review — 2026-09-06

Scope: HR-02/HR-04, local binary export/publication and descriptor revalidation.
The regression forced the first descriptor table hash helper to fail and observed
export return success. before-test.log preserves the failing assertion, and
before-result.json records its separate 300-second process-group deadline.
before-binary.sh, before-binary-package.sh and before-inputs.json identify the
exact pre-fix implementation/test bytes. This establishes false-success export;
it does not establish successful import of malformed metadata or lost payloads.

Descriptor construction previously embedded four hash commands in printf arguments,
which hid their failure statuses. Each digest is now assigned and checked before
metadata emission. The exported receipt's artifact digest is also calculated while
the bundle remains private, before its publication rename. This prevents successful
publication followed by an empty receipt hash. Successful descriptor and receipt
formats, standards pins and runtime dependencies are unchanged. Existing stderr
from the failed helper propagates without a new diagnostic format.

Oracle and forbidden outcomes: fail each package.tsv, target.kv, modes.tsv,
dependencies.tsv and artifact.kv hash during export. Require the injection marker,
nonzero exit, no stdout, no published bundle and identical target file/hash/mode
snapshots. Fail the four table hashes during import revalidation, requiring the
same rejection/preservation and no stage or record publication. The wrapper selects
only the hash-file helper and exact selected bundle-relative file; other commands
use the recorded host sh. Successful exports of base/app must emit exact receipts
whose hashes match the published artifact independently. Existing lifecycle tests
cover ordinary import, recovery and replacement with the shared descriptor helper.

Selected validation: scoped ShellCheck and the full sixteen-fixture suite under
its 600-second watchdog, including three pinned standards checks and whole-shell
lint. input-sha256.json records final dirty-tree runtime/test inputs; tools.json
records tool identities. Every attempted suite outcome remains in the raw logs.
No new test driver, runtime service or shared standard is introduced.

These are deterministic helper-failure injections, not physical full-storage,
power-loss durability, concurrency, hostile filesystem-race or remote-authentication
qualification. The previously tested public candidate predates this correction.
It needs refreshed assembly and qualification before receiving these claims.
Captured builder setup, independent reviews, the monitored security contact and
publication approval remain separate release gates.

All sixteen fixtures, three pinned standards gates, whole-shell and scoped lint
pass. The nine new descriptor failures, exact successful export receipts and
existing replacement/recovery controls pass. Runtime/test hashes remain unchanged
after the suite; suite-result.txt records its duration and operational deadline.
