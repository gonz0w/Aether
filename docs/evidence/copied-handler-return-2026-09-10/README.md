# Copied handler return and escape — 2026-09-10

Extended the raw signal-copy handler fixture without kernel changes. The original
self-post now seeds R12 and the low 64 bits of XMM14, deliberately clears live
XMM14 in the handler, and verifies both values after each copied restorer returns.
The invocation helper preserves the original caller R12 on its stack. This is
selected-register evidence, not a full CPU or FP-state matrix.

The child-only invalid-frame case changes reserved byte8 of its actual inherited
720-byte payload, probes sigreturn on that frame, requires -22 and unchanged current
mask, repairs the byte, and returns normally. The parent returns through its untouched
private frame. In the deliberate omitted-corruption control, the valid frame resumes
the original continuation before recording rejection; child250/owner1820 catches
the missing witness. Independent saved-R12 and saved-XMM14 corruptions produce the
same exact failure. All three controls require zero reclaims.

The sigsetjmp/siglongjmp case escapes the inherited handler in both processes,
restores the original mask and accepts one further self-post/delivery. Omitting
saved-mask restoration produces child249/owner1820 with zero reclaims. Normal
handler return, invalid-frame repair and escape repeat two generations with
parent71, child72, dummy29 and six reclaims. Existing raw memory, TLS, endpoint,
identity and register checks remain in the copied continuation.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#copied-handler-return-selection--2026-09-10)
records ownership, forbidden outcomes, assembly/stack obligations and simplicity.
The implementation reuses the checked user-frame ABI and musl return mechanisms;
no kernel active-handler token, syscall, flag, allocation, dependency or service
is added. The rejection probe preserves its current RSP in R11 under the existing
invalid-return contract. Payload offsets follow the frozen native frame layout;
its pointer comes from the handler's compiler-established frame pointer. No pointer
escapes the handler. The scope includes one reserved-byte rejection, not a full
malformed-frame or mapping-race matrix.

The complete 104-case connections suite and five launch cases are selected on
frozen runtime sources, together with the host build (98 Python tests and Zig/pin/
workflow checks). Final reports and timings record exact commands, identities,
status and review budgets. All new controls require the named client/owner ordering;
generic panics and timeouts are not successes. No qualified runtime attempt failed.

Only copy-client.c and launch_smoke.py runtime sources changed from the preceding
native signal-copy packet. Kernel, Rust owners, shared adapters, backend and command
sources are unchanged. Prior full command/M4 execution remains historical. Released
pins, sibling sources and consumer acceptance remain unchanged. These witnesses do
not implement installed SDK fork or guarded descriptor publication; that composition
is the next step. Full dash and R1 remain unfinished.

The collector verifies the previous packet, frozen source hashes, pinned simplicity
snapshot and source/artifact archive readback. Native artifacts retain musl notices.
Formatting, compatibility and final checks have separate receipts. Manifest seals
the evidence packet; runtime.patch records changes against the preceding snapshot.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

All 104 connections and five launch cases pass within their review budgets. All
98 earlier kernel images are identical. Of the earlier payloads, 97 match outside
entropy; only the strengthened handler case changed. The backend is identical and
maximum copy owner remains 5,880 bytes within the 8,192-byte bound.

Archive readback verified 225 source files and 1,905 native target artifacts.
