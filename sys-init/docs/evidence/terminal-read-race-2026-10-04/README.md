# Terminal/read EOF race repair

2026-10-04, BG-067 / [decision0184](../../decisions/0184-terminal-transport-interleaving.md).
Maintained ABI24 owner read-path repair; no sibling, kernel/client or release-pin
changes. Existing ABI22 recipe and historical packets remain untouched.

The old owner observes terminal, then reads a channel in separate syscalls. A
child can exit after the first observation, sealing its empty request stream.
The kernel then returns0; the owner rejected0 rather than reobserving terminal.
A private existing cooperative yield after the nonterminal observation for final
helper peer1/generation5 reproduces this on the actual matching kernel/client.
A delayed trace identifies the read check; a second value-instrumented immediate
trace records actual0 after slot2/generation5 terminal, then failure before parent
completion/halt. This is a real EOF witness, not a manufactured syscall result.
Selected sealed primary kernel source supports the transport/close semantics;
`contract-review/` is a bounded source review, not fresh SDK/kernel compilation.

The maintained repair requires a fresh terminal observation for the same owned
peer on read EOF. Existing terminal machinery validates/translates its observed
status, updates pipe/child state and clears cached transport frames. Reclaim occurs
only if already collected; otherwise normal wait/reply delivery and subsequent
cleanup continue. EOF itself conveys no authority or completion. A still-running
peer and other unexpected read errors retain the existing failure path. The fresh
frame borrow after observation preserves exclusive Rust buffer access. No new
state, unsafe site, retry, reply replay, status fabrication or resource quota.
WriteEPIPE handling is unchanged and unqualified by this scoped read repair.

Four fresh native positives compare exact90 UART bytes, eight admission identities,
ten terminal/reclaim identities, phase-relative cleanup/input and authorized halt:
maintained immediate/delayed and privately yielded repaired immediate/delayed.
Delayed cases wait35 seconds at the first prompt and two at subsequent prompts.
The unchanged independently authored producer oracle checks these exact traces;
receipt labels are normalized only in copies for immediate/delayed delay checks.
Two real native failures before repair remain distinct from acceptance witnesses.

Two additional controls preserve denial: an actual wrong read-endpoint direction
returnsEBADF9 and fails without successful halt; a private deliberately synthetic
read0 for the still-running final child fails required terminal confirmation.
The latter tests the safety gate, not native generation of EOF. Both stop before
final helper exec/admission/terminal and parent completion, preserving owned
unknown resources without successful halt/replay. Exact pre-completion UART,
previous identity sets, marker/result/line order and emulator reap are checked.
Ten altered failure traces (wrong diagnostic, removed terminal, false halt) reject.

The source/tools and selected sealed inputs were verified/frozen before private
compilation. Explicit Rust1.98.0/LLVM21.1.8 and pinned QEMU/xorriso commands are
retained. Builds are offline artifact composition, not fresh whole compiler/SDK
dependency audit. Payload readback matches composed bytes. All six linked owners
pass raw/ELF equality and scoped stack/immutable builtin inspection. Maintained
code15120/16384 bytes (64-byte increase), stack3816/4088 unchanged; private code
16064–16160 bytes and3912 stack.34 builtin indirect sites per image remain bound
to immutable memcpy/memset/memcmp. No formal CFG, corruption or kernel-stack proof.
New artifact archive members are read back against sizes/hashes. Unchanged boot/
firmware/client inputs and their original third-party notices remain in the
[owned candidate packet](../owned-serial-session-2026-10-03/README.md).

Each native case uses a private single-CPU TCG guest, separate flash variables,
90-second deadline,1MiB UART/4MiB stderr caps and group reap. Cases include concurrent
host execution but do not claim SMP, other-platform or exhaustive timing coverage.
Native failures, two Rust borrow-rejected source attempts and the initial oracle
line-boundary error are retained separately. The oracle initially assumed every
diagnostic began a raw line; negative output can follow `$ ` without a newline.
Exact token/count/order plus exact UART-prefix checks correct that assumption.
No native trace or earlier immutable evidence is rewritten.

The first historical failure's exact caller was never captured. The reproduced
failure has compatible helper terminal/UART boundary and now a concrete read EOF
cause, but that cannot prove exact historical attribution or all transport races.
The known race is repaired. Next maintain the offline candidate recipe/guide and
finish remaining composition/cleanup qualification. No complete v1, unlimited
shell, generic restart/recovery, operator CLI or release acceptance follows.

Six complete boot-directory readbacks verify all five non-owner boot components
against the sealed kit receipt, verify modified payload bytes and preserve client/
spare/entropy prefixes exactly. `readback.py`, raw logs and `boot-readback.json`
retain that check; this does not merely assume xorriso left other modules intact.

All ten repository gates pass in `out/checks/run-1cw6dfm_`, checked sources
unchanged. Aggregate and raw gate logs are retained in `validation/`. The changed
compiler-consumed maintained sources still match their pre-build snapshot. Native
boundary review, borrowed source provenance, coverage, guidance and scoped shared
standards records were updated before checks; no invented independent sign-off.
