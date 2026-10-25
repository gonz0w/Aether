# UL-059 pure runner parser evidence

The new C17 helper validates the complete AERUN001 carrier and selects copied
child arguments plus the fixed environment. It has no allocation, transport,
command lookup, printing or native authority effects. Only successful decode and
AR_LAUNCH publish output. Other outcomes preserve the prior output; callers must
not treat stale output as a launch request.

Final `parser/controls.stdout` records 1,293 assertions under UBSan. The 19 action
cases cover help/version, optional delimiter, missing/empty/slashed commands,
child options, empty/space/metacharacter arguments, four/five child bounds and a
31-byte argument. Corruption cases exercise every shorter carrier length, one
longer length, counts, magic/reserved/unused bytes, all active slot terminators
and padding, invalid typed input and unchanged output. Copies remain intact after
source mutation. These are deterministic checks, not an extended fuzz workload.
Both semantic mutants compile successfully and exit90 at their exact oracles:
skipped reserved validation, and child help wrongly treated as runner help.

The native object is ELF x86-64 relocatable, importing only memcmp, memcpy,
strchr, strcmp and __stack_chk_fail. No native link, boot or public CLI test was
performed. The existing host suite passes ten normal and eleven injected cases;
ordinary adapter, finite runner and native drivers were not changed.

`attempt-1/` and `attempt-2/` retain earlier passing parser runs; the driver then
received line wrapping and the contract gained scoped progress documentation.
`parser/` is the final run against current code and contract. No failed run in
this slice. `host/` retains the command regressions. `quality/` records C format,
Python 3.10 grammar (actual interpreter 3.14.7), and the three pinned standards
checks/documentation inventory gate. Successful checks do not imply reader review
or publication acceptance. `sources/` contains the final changed files, while
individual parser runs retain their exact consumed source/plan snapshots.

Every owned command uses an explicit environment, 30-second deadline (quality
60 seconds), a 16 MiB per-output-file limit and checked group cleanup. Compiler,
SDK, sanitizer runtime, sources, argv and actual dynamic dependencies are retained
in run records. ASan remains unavailable from the earlier empty-main timeout;
UBSan was explicitly selected, without waiving UL-062. Original code is BSD-2-Clause;
no new third-party runtime package was adopted.

Current-task technical review (Codex) examined validation ordering before string
access, byte-count shifts, fixed bounds, lifetimes, publication and caller failure
obligations. Independent technical/reader reviews are pending. Applicable scope:
Foundations O/I/E, approved CE/CC/CP, TD/TC/TE and DW/DM/DG; no standards pins,
authority contracts or product output changed. UL-059 stays active for opt-in
native carrier consumption, independent full startup observation, result mapping
and zero-admission/recovery owner acceptance. Evidence is invalidated for reuse
by any affecting source, contract, tool or plan change; no performance, whole-system
security or POSIX conformance claim is made.
