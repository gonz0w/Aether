# UL-058 bootstrap controls, CB-01–07 and CB-14 subset

Plan before implementation: link actual native-io.c to scripted host getauxval /
channel_raw / channel_yield seams. Each scenario is a fresh process. Exercise
parent/child generations 1/2; each first/second reference/FD/right corruption;
status/trailer/generation; missing/equal channels; EOF at 0/1/4/16/31 bytes;
successful re-entry and failed-startup retry/exchange. Independent byte counters,
reference values, EBADF, errno preservation and sentinel are the oracles.

Use pinned Clang C17 with AddressSanitizer/UBSan and no recovery. Capture resource
runtime identity and link libraries. 30 seconds per owned process, clean env,
private build roots, default 16 MiB file limit. LeakSanitizer is disabled explicitly
on this host; no leak detection claim. Retain baseline failures before correction.
If failed-startup retry is exposed, add terminal attempted/poison state while
preserving successful re-entry and legacy transport bytes. Review source diff,
run all controls and early-publication/disabled-poison mutants with exact oracle
failure status. Run 21 existing host/control and nine native regressions after any
adapter change. Five ELF inspection required; changed hashes expected after fix.

Apply CC/CP, TD/TE, Foundations O/I/E. No public CLI, protocol, owner source/pin
or production reset interface changes. CB-08–13 and remaining native boundary
witnesses are separate follow-ons. Current task technical review; independent
technical/reader review pending. All attempts retained; quality gate required.

ASan adapter timeout is an instrumentation prerequisite failure: an empty main
compiled with the same runtime also times out after five seconds, with cleanup.
Initial smoke compiles missed explicit -isysroot and failed linking; corrected
ones retained separately. UBSan-only empty main passes. Select explicit
--sanitizer undefined for subsequent controls, not a silent fallback or ASan pass.
Address instrumentation remains incomplete (UL-062); no leak/bounds claim.

Actual review: current task checked the adapter diff: one attempt bit, common
failed-path poison, unchanged full-pair validation/publication, successful re-entry
returns before poison. Twenty-two original scenarios include 13 retained failures;
all 22 pass after correction, and two mutation oracles reject precisely. Existing
host 21 and native nine regressions pass; all five changed ELFs inspected. Format
and Python 3.10 grammar checks pass. Independent reviews remain pending. Host
injection proves local adapter behavior only; native failure injection is NOT RUN.
