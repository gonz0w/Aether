# Bootstrap failure controls — UL-058

Twenty-two UBSan host scenarios pass on the actual separately linked adapter,
including parent/child generations, malformed binding words, invalid generation,
missing/equal channels, truncated bootstrap and re-entry. Early-publication and
disabled-poison mutants both fail at the exact independent oracle (24 outcomes).

The original adapter failed 13 cases: failed bootstrap allowed channel traffic,
and all-zero channels allowed repeated auxiliary-value lookup. The fix records
one bootstrap attempt and poisons every failed initialization path. A repeated
call after success rejects without poisoning live bindings. Successful publication
still validates the whole pair before exposing either binding. The adapter diff
and original sources are retained; no reset API, protocol or producer pin change.

All 21 existing host/control tests and nine native regressions pass; five fresh
ELFs are inspected and their changed hashes recorded. These native cases are the
legacy workloads, not new injected native bootstrap failures. NB-01–04 remain
open alongside remaining CB groups, independent reviews and public CLI adoption.

ASan's initial valid scenario timed out before output. An empty-main control also
timed out with the same instrumentation; UBSan-only empty main passed. Initial
smoke compiles omitted sysroot and failed linking; corrected attempts are retained.
No ASan or leak-detection pass is claimed. All timed-out groups were killed/reaped.

Raw attempts, source snapshots, sanitizer/compiler identities, process records,
mutant sources and final native logs are retained here. Large native images stay
under build/native-command-userland-wdbwcapa with recorded digests. The scripts
remain Python 3.10+ grammar; actual host interpreter is in each receipt.
