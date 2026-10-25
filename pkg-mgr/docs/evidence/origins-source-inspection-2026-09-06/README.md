# OC-H2 inspection evidence

2026-09-06. Local synthetic host-record inspection; no package/source authentication,
closure traversal, native runtime or producer/independent approval. Canonical local
interface: [inspection reference](../../ORIGINS-SOURCE-INSPECTION.md).

SOURCE-RECORDS.md.txt and source-review.json retain the producer proposal reviewed.
Attempt 01 passes 86 cases; attempt 02 adds string-escape/depth discrimination and
real closed-output handling, passing 89 cases plus help/version/usage checks.
Each retained case has input/output, expected code, subprocess status and input/
package-sentinel preservation. Shell-looking metadata remains inert; no marker is
created. File controls use the actual CLI and fixed five-second child deadlines.

The oracle is exact status/diagnostic or the independently checked-in result shape;
syntax/profile rejection must have empty stdout. Missing I/O and closed output are
separate errors. Every valid report says inspection-only with unresolved closure/
profiles and eligibility not-evaluated. No authoritative state is written.

Run python3 tests/origins-source-records.py; the normal sh tests/check.sh also runs
it. Required validations are the full host gate, scoped shell lint for the changed
gate and Experience integrity checks for the developer-command presentation.
Full-suite outcomes are recorded after completion. The ordinary manual compiler
example/native/TUF/storage qualification are not selected by this change.

Attempt 03 adds collection-limit, alternate-escape and ordered patch/helper controls.
All 96 cases plus help/version/usage checks pass. Each attempt retains its actual
harness/inspector identities; earlier smaller passes are not relabelled.


Final gate: sh tests/check.sh exits 0, including all sixteen shell fixtures,
13 OC-H1 cases, 96 OC-H2 cases and the required standards/lint/manual/watchdog checks.
Attempt 04 retains the actual integrated OC-H2 records; suite.log and result.txt
retain the overall result. No failed run occurred in this OC-H2 implementation;
earlier successful smaller corpora are retained separately. The binary compiler
manual example and native/TUF/durable-storage qualification remain NOT RUN.
