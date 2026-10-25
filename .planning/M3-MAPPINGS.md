# M3 transport mappings and ownership acceptance

The two-core user phase builds private page-table hierarchies instead of copying
boot upper-half entries. Map the linked kernel image with RX text, read-only/NX
constants, and RW/NX data. Do not retain the HHDM. A fixed 16 MiB kernel-image
bound fails closed if exceeded; this is not a general virtual-memory allocator.

Reserve exactly three page-aligned queue backing pages in a separate linker
section. Omit that section from the linked-image virtual mapping. Map only those
three physical pages at 0x01000000, 0x01001000, and 0x01002000, supervisor RW/NX,
with surrounding pages absent. The kernel probe uses the original aliases before
the switch; user IPC uses only the dedicated transport addresses afterward.
Flush inherited global translations when switching roots. No backing is reused.

Both CPUs verify transport PTEs, missing old aliases, missing HHDM root entries,
and absent neighboring transport PTEs before user execution. A negative image
that retains the original transport alias must fail. The AP worker first attempts
a user read of transport and must fault with protection error 5. The test handler
skips that known three-byte fixture instruction, then the existing APIC read must
fault and terminate the worker. BSP must continue advancing after termination.

Ownership review: each Core owns its stacks, descriptor tables, runtime/page
tables, capability table, syscall counts, and progress. Queue head has one
consumer writer; tail has one producer writer; slots are handed off by acquire/
release. Readiness/failure/completion fields are explicit atomic shared control;
AP result fields are published once with release/acquire. Bootstrap inputs and
CPU identities are immutable after handoff. M2 objects remain BSP-only. No shared
allocator or dynamic cross-core capability authority is introduced.

Kernel image data remains mapped to both trusted kernel instances. This layout
removes transport aliases and broad boot mappings; it does not sandbox a
compromised kernel or establish hardware protection between kernel instances.
