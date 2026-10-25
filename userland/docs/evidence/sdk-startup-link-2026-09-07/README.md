# Imported SDK startup/adapter link — UL-005, 2026-09-07

The imported musl SDK plus receipt-pinned io_probe.c and I/O/memory adapters
statically link with explicit crt1/crti/crtn and libc. The libc receipt identity
matches `libc_receipt_sha256`; live io_probe.c, native_io.c, native_memory.c and
memory_probe.c match that receipt before compile. A mutated io_probe is rejected.
ELF64 x86-64, no INTERP or DYNAMIC program header. nm may list `_DYNAMIC` only.
Omitted crt1 fails as a fatal missing `_start` warning. Omitted I/O adapter fails
on `__aether_io`. A missing memory object path fails. Unsigned 128-bit division
fails on `__udivti3`. Missing SDK headers and omitted libc still fail without
host fallback. No ELF was executed.

Earlier runs built probe.c without receipt hash checks; they remain valid only
for that recorded source set. This correction selects io_probe.c. Incomplete
crt1/`_DYNAMIC` oracles from the first slice are retained.

SDK-05 pinned startup/adapter/helper closure is corroborated for this imported
payload. SDK-07 stale-consumer rebuild and SDK-08 native execution remain open.
UL-005 stays active.

| Attempt | Result |
| --- | --- |
| sdk-startup-fghppact | omitted crt1 warning not fatal; incomplete |
| sdk-startup-jec05lug | nm `_DYNAMIC` treated as failure; incomplete |
| sdk-startup-qymeevz0 | pass for probe.c (not the receipt-pinned io probe) |
| sdk-startup-lefmmlgo | io_probe + receipt hash check + changed-source control: pass |
