# 0097 — I/O worker build tool bounds

Accepted bounded build fix, 2026-09-06; BG-056 CP-02/TE-02 follow-up to decision 0096.
The older I/O worker builder captures unlimited tool output and has no deadline.
Apply the existing service-worker runner's 180-second / 4 MiB bounds with owned
non-detaching process-group cleanup and retained accepted output prefixes.
Keep original successful evidence schema/commands and worker/compiler flags.
Add a separate attempt record before each command and on success/failure so a
failed tool cannot leave the attempt looking successful. Preserve timeout,
nonzero, output overflow and missing-tool classifications distinctly.

Reuse the small reviewed runner within this self-contained captured builder;
do not add a shared framework or an unrecorded imported helper dependency.
Run the real bounds/error controls against both builders. Build all four I/O
profiles from the retained verified SDK/tools and compare their exact worker ELF
and envelope with the corresponding accepted artifacts. If bytes differ, retain
the cause and obtain affected target evidence before any behavior claim.
No native source, ABI, release pin or sibling changes are authorized by this step.

## Results

Decision 0097 closes the older I/O worker builder duration/output finding.
Tools now have 180-second and 4 MiB bounds, owned process-group cleanup, retained
log prefixes and per-attempt running/pass/fail/timeout/output-limit/infra-error/
interrupted records. All four retained/readiness/authority/peer profiles rebuild
from verified offline SDK/tools to identical worker ELF and envelope bytes.
No new native execution is claimed or needed for identical artifacts.

Six real runner tests cover success/nonzero, missing tool, timeout and overflow
across both worker builders. All ten aggregate gates pass in
`out/checks/run-fcjtshwd`; native inputs and release pins are unchanged.
Other older supervisor/lifecycle builders, complete Python/C path review,
extended scheduling and independent technical/reader review remain open.
