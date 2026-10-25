# SDK-08 isolated snapshot and first native attempt — 2026-09-07

An isolated Aether/sys-init source snapshot (206 + 36 files, no evidence
tarballs) was captured under build/. The selected imported-SDK io_probe ELF was
packed as AENATC01. Supervisor wrap and zig -Dsmp=false -Dnative-memory succeeded.
QEMU io_smoke did **not** pass: serial shows memory admitted, then
`NATIVE supervisor result=214 reclaimed=0` and `AETHER PANIC: native C profile
rejected`. Code 214 is the current io supervisor's EAGAIN overflow check
(`0x20008` byte 99). The imported-SDK consumer is therefore not accepted on this
producer. Historical 2026-09-05 contract still does not match
(`44d449…` vs `a0b977…`). Native SDK-08 remains NOT RUN as acceptance.

| Attempt | Result |
| --- | --- |
| sdk08-native-1g60t3by | snapshot+pack+boot; supervisor 214; profile rejected |

Do not weaken the supervisor oracle. Next: a producer/consumer pair whose io
stream semantics match, or an isolated snapshot of the original native-memory
producer. Live sibling tree is still not selected. UL-005 stays active.
