# Replacement scratch-table restoration — 2026-09-15

The private C helper restores a committed survivor table into a fresh descriptor
adapter after its three-stream bootstrap and validated scratch grant. It validates
all64 table bytes and two16-byte description records before mutation. Descriptions
supply reference, mode, exact local alias count and zero reserved word. This is
local helper input; no native transport extension or public SDK is adopted here.

The deterministic host witness covers parent and child references, shared writer
aliases, an independent reader, empty/full tables, repeated restoration, wrong
owner/process/peer/slot, noncanonical records, count/mode mismatches and CLOEXEC
survivors. Every rejection checks all descriptor/binding arrays are unchanged,
errno and mask balance are preserved, no backend request occurred, and the
connection is poisoned. The helper does not itself grant owner authority or
close backend holders.

`focus.json` records the positive and two compiled controls. Omitting stale-reference
validation or accepting CLOEXEC survivors must fail the exact rejection assertion
with exit90. No unexpected failed attempt occurred. `native-compile.json` records
successful object compilation against the existing pinned native musl SDK.
`host.log` records successful Zig tests, all104 Python tests and offline standards
checks. `checks.json` records C formatting, workflow and simplicity snapshot checks.
Run the existing `zig build test --cache-dir .zig-cache --global-cache-dir
.zig-cache/global`; exact focused compile commands are retained in focus.json.

Scoped source and binary archives have per-file inventories; every member was
verified, and only the archived duplicate binaries were removed. `source-delta.json`
confirms the only modified input from the last native qualification is the host
C witness; no native profile includes the new header yet. The prior335-case native
receipt remains scoped to its recorded bytes. No new QEMU or exec result is claimed.

Next: native owner exec admission, CLOEXEC holder release and replacement bootstrap
publication, then full affected connections/matching runner and unchanged dash
fd-leak-control/redirection. Failed-exec retention and poisoned-close recovery
need native evidence. Independent SDK/consumer acceptance, persistence and R1
assembly remain open. Sibling repositories, released pins and native limits are
unchanged. SHA256SUMS seals this packet; do not overwrite it on replay.
