# Host transfer and reply controls — UL-058

53 scenarios and two semantic mutation controls pass with explicit UBSan on the
actual separately compiled native-io.c. Coverage includes short/EAGAIN progress,
zero/fatal/overlong transfers, exact 100000-turn exhaustion, partial/dropped reads,
lost/negative/padded close, every metadata byte and unused read-data padding byte,
signed error boundaries, invalid frame sizes, valid short write and consuming
close. Independent scripted request bytes, destination sentinel, errno and zero
subsequent transport calls are required. Valid negative replies leave the
connection usable. No adapter implementation changed.

The no-replay control rejects any later file/launch/collection channel call;
test-only removal of transfer poison fails precisely there. Test-only disabled
reply validation fails the result oracle. Its initial compile failed because the
mutation left bad unused under -Werror. The revised mutation retains that
variable's use and fails semantically at status 90. Both attempts are retained;
compile failure did not count as a passing mutation. All 24 bootstrap and 21
existing host/control regressions pass on the final harness.

These are fresh host processes and a scripted peer, not native service completion
or remote cleanup proof. A dropped reply follows a completely captured request;
no assertion about real service side effects follows. Prior native regressions
are not rerun: adapter and native driver bytes remain unchanged. ASan remains
incomplete from the earlier empty-main timeout; no address/leak pass is claimed.
NB-01–04, independent reviews and UL-059 native/public integration remain open.

Raw reports contain compiler/runtime identities, source/plan hashes, argv,
environments, deadlines, exits and owned process cleanup. No source/SDK install,
producer pin or shared contract changed. Python 3.10 grammar and pinned C formatting
pass; actual interpreter/platform are in the receipts.
