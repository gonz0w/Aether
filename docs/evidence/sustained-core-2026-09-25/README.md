# SI-07 serial mechanics and real-command blocker

Status: **experimental implementation; real-command composition blocked**.
This packet is an exploratory checkpoint, not a qualified SI-07 producer handoff,
consumer acceptance, merge qualification or release readiness. The pre-code design,
selected serial authority, operation contract and remaining gates are in
[the canonical reference](../../NATIVE-INIT-COMMAND.md#si-07-sustained-profile-review--2026-09-25).

## Results

- Six sustained state-core tests pass in the final host suite; the initial five
  also passed standalone Debug/ReleaseSafe. Final optimized coverage includes the
  added serial-status test through the channel test module. They cover disjoint
  identity fields, finite exhaustion, both event orderings, serial level readiness,
  spurious polls, deadline ties and retained cancellation/completion. Added channel
  tests cover high generations, holder enforcement, last-close zeroing and retirement;
  envelope tests cover the separate three-image framing. Host tests do not establish
  scheduler atomicity or grant enforcement.
- The final native mechanism probe passes with 3005 total ticks and 3004 kernel idle
  ticks, six channel lifetimes, stale-channel denial, event/halt grant denials,
  unsupported-action and busy-halt rejection, actual serial input, UART closure and
  final authorized halt. No worker was launched in that particular probe.
- The real runner/bytecount/backend completes two cycles: terminal statuses 0/0/17,
  exact backend `6\n` readback and original cleanup checks. At generation 3 the
  admitted runner exits 110. This is a failure, not five-cycle acceptance.
- The existing five-case bounded command suite passes on the changed kernel:
  positive, empty, fault, wrong role and omitted close. Broad capacity/connections/
  runner regressions have not been rerun for this prototype and remain required
  before merge or a completed producer handoff.

## Consumer dependency

`consumer-blocker.json` binds the frozen and current sibling copies of
`four-role.c`, `runner-result.c` and `native-io.c`; all three remain identical.
Each explicitly restricts generation to 1/2. The role decoder causes the observed
runner startup exit 110; the other restrictions would also prevent sustained reuse.
No sibling or immutable consumer file was modified.

Userland must supply a versioned sustained carrier/admission/native-I/O contract,
matched rebuilt runner and bytecount inputs, and stale/exhaustion rejection oracles.
Private file-reference fields begin at bit 16, so merely allowing the kernel's
28-bit generations would alias private identities. Native lifetime, protocol epoch
and ownership must stay distinct. After this delivery Aether can finish the useful
five-cycle test, shutdown with settled work, native race/foreign-worker controls,
fresh input builds and matching regressions. Sys-init then consumes using its own
supervisor; this reference fixture is not that supervisor or its policy.

## Inputs, stack and failures

The exploratory native images reuse the hash-verified `parent.elf`,
`positive-backend.elf` and `child.elf` from the **passing**
`zig-out/init-command-36kp9xup` members of the sealed 2026-09-08 command packet.
The first archive selector failed because that packet contains two attempts; the
correct passing source was then selected explicitly. The legacy regression freshly
rebuilds its inputs with the pinned SDK and tool lock. `command-build.json` records
the new owner's raw/ELF commands; AETHER_RUNNER_STARTUP names the preserved startup
record. Native source manifests and serial/process receipts identify each run.

The final command owner is 8496 bytes within the existing 16 KiB code budget.
Linked inspection reports 3768/4088 usable stack bytes (320-byte margin), including
the fatal fixture path. Immutable GOT cells 0x402118/0x402120/0x402128 bind
memset/memcpy/memcmp at 0x401d30/0x401d00/0x401d80. Register-indirect call sites load
those cells (rbx at 0x4002a5 and 0x400b1f; r13 at 0x4002e3; rbp at 0x400e08).
The inspection aid charges the maximum memory builtin path. This is scoped linked
inspection, not a formal proof, independent reader review or whole-kernel bound.

Retained unsuccessful attempts:

- Initial standalone Zig test omitted local cache paths and failed permissions;
  the corrected Debug and ReleaseSafe commands pass.
- Initial host wiring check detected an unclassified new boolean build flag;
  it is now explicitly classified as a profile opt-in, not a negative bypass.
- Ambiguous historical artifact selection failed before constructing the envelope;
  the subsequent image build consequently failed on the missing input file.
- The first command owner link used the old 8 KiB linker and rejected its size;
  the existing 16 KiB connections linker matches the new profile's declared budget.
- First command run timed out after runner generation-3 exit 110: its old error path
  invoked unsupported fixture finish and spun. The new-profile fixture failure path
  now emits an explicit failure and faults; the second run reproduces exit 110 and
  fails promptly. Neither failure is reclassified as success.

Retention limitation: the first command attempt's ISO/raw owner were overwritten
by the diagnostic repair before archive capture. Its complete source snapshot,
hashes, serial log and process receipt remain, but these do **not** reproduce its
original artifact bytes. Available final artifacts and every retained log are
archived. This is an explicit evidence gap; do not promote this exploratory packet
to qualified all-attempt evidence. Future qualification uses separate attempt roots.

## Commands and boundaries

Host: `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.
Core: `zig test kernel/native_sustained.zig` with those same cache options and
optionally `-O ReleaseSafe`; channel ReleaseSafe coverage uses
`kernel/native_channel.zig`. Native probes require the corresponding archived
prepared image directories; see `run-probe.py`, `run-final-probe.py`,
`run-command.py` and their receipts. A fresh PROBE_ATTEMPT avoids overwriting logs.

The private probe uses `h` as a test input. The reference command probe uses five
`r` bytes followed by `h`; neither is a public shell/init command language. Kernel
code does not interpret these bytes. UART, event observation and final halt remain
contextual supervisor authorities; runtime operations are unavailable in old
profiles. Released standards pins and previous evidence are unchanged.


Closeout correction: the new UART readiness polling initially read LSR without
retaining read-cleared errors. TI TL16C550C section 7.7.8 explicitly describes that
behavior for bits 1–4. The corrected selected-profile status latch preserves errors
across both receive and transmit polls until readByte returns LineError/EIO. Legacy
non-monitoring behavior remains unchanged. A host counterexample covers each error
bit and a transmit poll between detection and consumption. Hardware error injection
remains missing coverage. The final-byte QEMU probe is attempt 3; earlier attempts
are retained and are not silently relabelled as the final source set.
Source: https://www.ti.com/lit/ds/symlink/tl16c550c.pdf (section 7.7.8).

The first closeout workflow inventory mistakenly placed evidence-only helpers and
a build flag in inventories reserved for canonical scripts CLIs. Its failing host
log is retained. The corrected inventory records the experimental build selection
and prepared-image helpers in AT-SUSTAINED-NATIVE without weakening the checker.
