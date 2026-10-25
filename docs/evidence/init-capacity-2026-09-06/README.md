# SI-05 init-compatible capacity — 2026-09-06

AENIN002 / ABI 15 is a separate BSP-only init profile with 1–8192 supervisor
bytes. AENIN001 / ABI 6 retains its 4096-byte maximum. The new profile retains
worker slots 0/1, supervisor slot 2, the two executable grants, factory, channel
and observation grants, and the existing init operations and lifecycle semantics.
The exact contract is in the retained contract.md and docs/NATIVE-INIT.md.

Code occupies one or two immutable RX pages starting at 0x400000. The separate
stack is RW/NX. The loader verifies code flags, every kernel code alias and zero
unused tail before entry. V2 uses distinct LARGE PASS/CLOSED markers. Normal
completion still halts with the supervisor mapped; fail-closed shutdown detaches
all domains and verifies all backing cleared, including both supervisor pages.

## Qualification

All 207 selected target cases pass, including 23 v2 cases and nine unchanged
ABI-6 cases. V2 executes the complete init workload from page two using a first-page
jump and a supervisor linked at 0x401000. It checks deadline behavior, owner exit/
fault, sequential reuse and reversed reuse, and exact cleanup rejection controls.
Boundary positives cover 4095, 4096, 8191 and 8192 bytes. Zero, 8193, u32 maximum,
reserved, truncated and excess payloads reject before entry; old ABI 6 rejects the
oversized v2 payload. Dirty code tail rejects before entry. Actual page faults
verify second-page writes (error 7) and stack execution (hex error 15), followed by
complete fail-closed shutdown. Signal delivery and supervisor recovery are not added.

Old launch/channel/files/process/program/connection/command profiles, console
relay, both pthread lifecycle and memory profiles, image loading and M4 regressions
pass against the changed kernel. Host checks pass 97 Python tests, Zig tests,
offline standards/workflow and Zig/Rust formatting. final/results.json records
exact commands, UTC boundaries and frozen source hashes. Sources are checked
before/after every command and before archival.

The initial target run failed because the new NX oracle compared a hexadecimal
fault diagnostic against decimal 21. The actual fault and cleanup were correct;
the failed attempt remains retained. The corrected initial run passes all 23
cases. All 20 attempt directories are retained, 18 from final qualification.
No sys-init source, existing consumer pin or immutable standard changed.

## Producer bundle and independent consumption

producer.json identifies the exact profile, source/SDK archives and qualified
positive envelope/ISO. producer-source.tar.gz contains regular build sources,
tests, documentation and the pinned boot dependencies, with producer-source.json
covering every file. sdk-inputs.tar.gz retains the strict native SDK and musl source;
tools.lock.json and tool-identity.json record required installed tools. Tool binary
identity is not a claim of complete toolchain library closure or independent build.
The target archive retains ELFs, raw supervisors, envelopes, ISOs and serial logs.
All local packet files are covered by SHA256SUMS.

To reproduce in a fresh private source directory, extract producer-source.tar.gz
there and sdk-inputs.tar.gz in a separate private SDK directory. Use the matching
installed tools recorded by the lock (review/pin different paths explicitly):

```sh
python3 scripts/launch_smoke.py --init-large --libc-build /ABS/SDK/native-c-5olokhku --tools-lock /ABS/PACKET/tools.lock.json
python3 scripts/launch_smoke.py --init --libc-build /ABS/SDK/native-c-5olokhku --tools-lock /ABS/PACKET/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Sys-init must review ABI 15 and markers, explicitly pin this bundle, rebuild its
151 existing semantic cases and qualify its proposed guard cases. This packet is
producer evidence, not that independent acceptance or permission to change pins.
Independent reviewer and extended/hardware coverage remain outstanding.

The maintainer requested this one unblock and then a return to planned work.
Next in Aether: bounded concurrent child slots and all-child observation/cleanup.
UP-02 handoffs remain queued; no additional companion diversion is implied.
