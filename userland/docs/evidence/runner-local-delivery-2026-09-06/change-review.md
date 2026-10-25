# UL-059 host local-output delivery plan

Before code: add a host-only command-specific candidate accepting one of the six
proposed local actions and its already-selected immutable text. It does not select
commands, issue admissions, allocate native roles, implement a POSIX write API or
activate the public runner. Logical sink labels are callback routing data, not
capabilities. Fixture hashes must match the retained proposal before consumption.

A single-use state records original intended exit/error, confirmed delivered bytes,
write failure and separate close outcomes for both caller-owned logical sinks.
Positive writes advance only their suffix and bound attempts by message length
(max512). Known zero/error ends writes, then consumes both closes once. Unknown or
malformed callback results stop all calls on the shared connection immediately;
remaining closes stay unattempted. Close failure cannot erase original action/error;
close unknown stops the other close. Re-entry performs no effects. The callback
contract supplies explicit known/unknown, count and error; no successful no-op
stands for unsupported native I/O. Valid input requires live disjoint state/text/
callback context and both roles already owned; no concurrency or arbitrary pointer
validation is implied. Invalid initial input produces exit1 and no effects.

Test exact fixture bytes and sink separation for six actions, every positive chunk
size and failure prefix, known zero/error/unknown writes, malformed callback facts,
each close error/unknown, invalid plans and repeated use. Four semantic mutants
must reject suffix replay, ignored close failure, write after unknown and wrong
sink. Use pinned Clang21.1.8 strict C17/UBSan host30s/file16MiB, Python3.10+ owned
process helper, pinned format and quality gate. Run affected parser/result/mapped
and21 command host regressions. No native behavior or producer changes: prior native
receipts are referenced, not rerun or relabelled. Retain all attempts and original
source/tool/fixture/plan hashes. O/I/E, CE/CC/CP, TD/TC/TE and shared Experience
stream/plain-output requirements apply. Current-task review only; independent and
owner reviews remain pending. Original source BSD-2-Clause; no new dependency.

## Contributor CLI review addition

Initial host algorithm run _77abthe passed all6130 scenarios/four mutants. Before
completion, adopt required help/version/usage64/plain behavior for the new checker,
preserve child test markers, escape diagnostic control bytes and use bracketed
status labels. No color/animation is emitted. Repeat the affected checker and
exercise CLI stdout/stderr/exit controls including invalid control-character input.
The first passing algorithm attempt remains retained; this is presentation
completion, not a runtime defect or native renderer acceptance.
