# Preflight producer/sort failure review — 2026-09-06

HR-02/HR-04 found three POSIX pipeline seams where failure in a comparison or
path-list producer could be hidden by a successful downstream sort/reader.
The regression added before the fix reproduced a successful raw preflight despite
an injected update-diff failure. before-test.log retains that failing assertion;
before-binary.sh, before-observe.sh and before-input-sha256.json identify its inputs.
This was a false successful/incomplete preflight, not an observed payload mutation.

The fix materializes comparison output in the existing private binary scratch
root before sorting. Observation now creates its own private scratch directory,
checks path extraction and sorting as separate commands, then reads the completed
path list. Ordinary shell failure stops each script. Observation scratch is owned
by its exit trap. Successful report format and ordering remain unchanged; no new
runtime dependency, package format, pin or live-prefix authority is introduced.

The oracle requires nonzero failure, no emitted report and unchanged target files,
permissions and records. Twelve cases inject empty or partial output followed by
exit 73 at diff, three-way, observation and each corresponding sort. Each must
reach its injection marker, reject before the public report and preserve the
complete target file/hash/mode snapshot. Existing successful comparisons and
local/configuration conflict cases provide the positive behavior checks.

input-sha256.json records final runtime/test inputs. Scoped lint passes without new
exceptions. All sixteen fixtures and three pinned standards gates pass with the new cases.
The final full-suite log and result, plus follow-up standards,
development and whitespace checks, are retained with this review. The original
failed regression is preserved separately, not counted as passing evidence.

This is bounded process/tool failure evidence, not actual disk exhaustion, physical
power loss, hostile path races, concurrency safety or independent release review.
The earlier public archive predates this runtime change and needs refreshed
assembly/qualification. Pinned setup, independent review, the monitored security
contact and an explicit publication decision remain outstanding.
