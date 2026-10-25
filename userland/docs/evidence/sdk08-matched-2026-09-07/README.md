# SDK-08 matched producer native evidence

The retained UL-044 kernel snapshot exists and matches all 4557 source hashes in
the selected SDK native receipt. Its NATIVE-C contract hash is 81f802d1..., distinct
from both the earlier closure's native-memory lead and the live-tree attempt.
Reviewed NATIVE-C/IO/MEMORY selects unchanged bounded stream/grant semantics.
Each run makes a fresh build-only copy and uses the previously isolated 36-file
sys-init snapshot. The supervisor overflow oracle and owner sources are unchanged.
This does not diagnose the earlier live-snapshot supervisor214 failure's root cause.

The imported-SDK io_probe ELF remains d804589d... and is packed with the original
SDK envelope's developer bootstrap bytes. Final run sdk08-matched-rabs9oe_ passes:

- Positive: two detail0 terminal generations, supervisor100/reclaimed2, IO PASS.
- Withheld memory grant: worker detail61, supervisor211/reclaimed0, exact native
  profile-rejection panic, no IO PASS. Host QEMU/process cleanup completes.

Positive native reclaim is demonstrated. Denial native reclaim is not: its
supervisor reports zero reclaims and the guest panics. Do not substitute host
QEMU teardown for guest resource-reclaim evidence. This is the first bounded
pass/denial/positive-cleanup slice, not the full historical suite or production
SDK/native acceptance. Package SDK-07 integration and independent review remain.

The first matched attempt sdk08-matched-enanyosn passed positive and reached
worker61 on denial, but its harness incorrectly required IO FAIL. The selected
require() path emits an exact profile-rejection panic before that marker. The
amended plan requires worker61 plus supervisor211/reclaimed0 and the exact panic;
both cases were rerun. The incomplete attempt and its original driver/plan remain.

All consumed kernel/sys-init source copies are checked after the final run.
Boot inputs verify through their pinned manifest; Zig/Rust/QEMU executable hashes
match the existing tool lock. result.json retains final artifact/driver/plan/tool
identities. Per-attempt command receipts retain argv, env, timeouts, raw streams
and complete owned cleanup. Source inventories, serial logs and snapshot locations
are retained; ISOs/payloads stay under build/. No live sibling execution, source
edit, dependency download or package mutation occurred. Historical evidence stays
unchanged. Quality checks are recorded separately from these native results.
