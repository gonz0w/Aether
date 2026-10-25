# Host accounting evidence — 2026-09-05

Scope: BG-028/BG-054 validation of existing bounded observation, launch and cleanup contracts. No runtime, model or shared release changes. Foundations E-04/E-06 apply through the pinned adoption; lifecycle ordering remains owned by sys-init decisions 0002–0005.

Run `python3 scripts/check-all.py`. The [combined report](positive/results.json) records exact commands, host/Python and source hashes. All three standards checks, 34 model cases/three mutation controls, 35 host cases and 10 harness cases pass on macOS. Adjacent logs preserve each result.

Three new test methods (including two real exec-error subcases):

- Eight one-shot children exit normally with distinct codes or terminate themselves with SIGTERM. The test waits using each owner's Popen object before pumping, then checks exactly 24 observations: eight launches, eight terminal results and eight cleanup acknowledgments. Each cut has at most four observations. Every generation has its expected completion/detail, and no child or readiness descriptor remains owned. This tests accumulated statuses across bounded polling cuts; it does not test a SIGCHLD handler, delivery count or independent wait ownership.
- A malformed executable image and a script naming a missing interpreter pass file/hash prevalidation but fail real process creation. An os.pipe wrapper records actual allocated descriptors; all are closed after failure. Failed launch never becomes started, admits no dependent and completes modeled reclamation. These are OS exec errors, not simulated return codes.
- A pinned executable changed after runtime construction fails revalidation before Popen is called. This tests accidental changes in a trusted workspace; it does not close hostile filesystem races.

[Negative controls](negative.json) use independent disposable source copies and the recorded unittest command. Misclassifying signal death as normal exit fails one assertion. Leaving the launch pipe writer open fails two exec-error subcases. Their logs are adjacent. These are expected assertion failures, not watchdog or missing-runner outcomes; the copied worker's exit closes deliberately leaked test descriptors.

Native Aether execution, Linux/BSD/illumos, authenticated launch, exclusive-wait enforcement and crash containment are not established. Existing parent-death survival evidence remains valid. BG-028 retains helper ownership, measurements and enforcement decisions; BG-054 retains cross-host/CI work.
