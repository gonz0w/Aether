# Incomplete final publication — 2026-09-10

After validated child readiness, the owner sends complete final success to one
client and zero or 16 of 32 bytes to the other. The incomplete client must emit no
application request during the existing 256-read-attempt observation. The complete
peer can observe success and queue an input request, so this is containment of a
partially published pair, not rollback of observed success.

The owner confirms both clients stopped143/kind3 before draining the peer's one
queued request or removing holders. Both response channels must then report EOF.
No application operation reaches the backend; the three known idle handles close
normally and the backend finishes17. Two generations yield six reclaims. Forced
client stops produce no normal user terminal serial lines. The attempt budget is
not a wall-clock deadline or fairness guarantee.

All 72 connections and five launch cases pass, plus 98 Python host tests and
Zig/pin/workflow checks. Four new positives cover missing/partial completion for
parent and child. Parent/child padding controls expose application traffic and
reject owner2001. Omitted parent stop rejects2002; omitted child stop rejects2003,
both before peer-request discard or reclaim. These controls require zero reclaims.
No failed attempt occurred. Connections-suite-lrdxn299 completes on frozen sources.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#incomplete-final-publication-selection--2026-09-10)
records ownership, forbidden outcomes, test selection, pointer obligations and
simplicity tradeoffs. Existing bounded reads, native stop, idle backend close and
dispose paths suffice. No retry frame is appended behind partial completion and no
new completion opcode, service, kernel primitive or pool is added. Whole-pair stop
is this bounded producer fixture's containment choice; installed SDK process
semantics and sys-init supervision policy remain separate.

Kernel, backend and command sources are unchanged. The ordinary backend image
matches the preceding slice byte-for-byte. The inherited-client image changes with
the completion-reader helper; all previous inheritance cases retain their oracles
and pass. Default parsing still requires all 32 bytes; only the deliberate padding
build accepts a short frame. The 22 older raw connection payloads match outside
48 fresh entropy bytes. Maximum owner size remains 5,880 within 8,192. Prior full
431-command/M4 runtime evidence remains historical. No siblings or released pins
changed.

Bounded descriptor snapshot validation before freeze/reservation, signal-aware
preparation, installed SDK fork/exec/wait and independent consumer acceptance remain
open. These producer witnesses do not complete full dash or R1.

Timings retain exact commands, UTC timestamps and exit status. Reports bind source,
tool and SDK identities. The collector verifies the preceding packet, frozen inputs,
pinned simplicity snapshot and archive readback. Native artifacts retain musl
notices. Formatting, compatibility and final checks have separate receipts;
manifest.json seals this packet.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Archive readback verified 225 source files and 1,361 native target artifacts.
All final suites met their documented review budgets.
