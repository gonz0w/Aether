# Native serial console v1

R1-01 implementation contract, recorded before code on 2026-09-06. Experimental
BSP-only COM1 transport, not shell, TTY, line discipline or release acceptance.
Aether owns enforcement; userland owns terminal policy; sys-init owns eventual
service startup. No dependency, arbitrary device access or POSIX claim is added.

The AENSC001 envelope uses the AENSUP01 layout and lifetime. Its bootstrap owner
receives ABI 10 in RDI, factory in RSI and a caller-bound console grant in RDX.
Only that initial owner has the grant; a worker copying its integer has no rights.
The grant is not transferable in this version. Close is permanent until reboot;
owner termination also makes it inaccessible. No replacement console owner or
buffer inheritance is implied. Other profiles expose no console operations.

int 0x81 operations use RDI=grant, RSI=buffer, RDX=count:

- 0x26000 reads raw bytes; 0x26001 writes raw bytes. Requested count 0..256;
  each call transfers at most 16. Validate the complete attempted span before any
  UART effect. Zero count ignores the pointer and returns zero after authority.
- 0x26002 closes the grant (buffer/count ignored).
- Wrong caller/grant returns -13; closed grant -9; excessive/overflowing count or
  invalid attempted memory span -14. Unavailable RX/TX returns -11, or a positive
  short count if progress was already made. RX line errors return -5 if no progress;
  the errored byte is discarded. Empty UART is never EOF. No waiting in the kernel.

The interrupt gate serializes this BSP-only access. Every byte uses validated
local mappings, RX requires writable pages, TX readable pages. No allocation,
retained kernel console queue, DMA or user port permission. Each call checks at
most 16 bytes. The hardware FIFO can overflow if userland fails to drain it;
this polling slice does not promise lossless paste. Diagnostics still share COM1
and preserve their bounded emergency path; normal output/diagnostic separation
and an interrupt-driven console service remain integration work.

Forbidden outcomes: access by an ungranted worker, effects before buffer checks,
successful dropped writes, empty-read EOF, access after close, altered old ABIs.
Test plan: real QEMU bidirectional serial exchange including NUL/ESC/CR, EAGAIN,
short transfers, bad pointers/counts/grants and read-only destinations, worker denial across three
launch/reclaim generations, close denial, deliberately wrong response rejected;
host checks and existing default/SMP and native channel/supervision regressions.

Run:

```sh
python3 scripts/console_smoke.py --libc-build <strict-sdk> --tools-lock <pinned-tools.json>
```

It builds a Rust bootstrap owner and C denial witness and
retains commands, hashes and raw serial logs. This is a transport witness, not a
replacement public shell. See STATE for execution status and evidence.

## Exclusive handoff v2 (contract recorded before implementation, 2026-09-06)

AENSC002 uses the same envelope layout, bootstrap ABI 11 and initial grant.
It adds 0x26003: RDI=console grant, RSI=live child handle, RDX=0. Only the
initial bootstrap owner may move its still-open grant, once. Success returns 0
and atomically removes bootstrap access while binding the grant to the exact
child slot and generation. The child uses the v1 grant selector 0xf001; that
selector is inert without the kernel-owned binding. No auxv mutation, new memory,
queue, scheduling operation or POSIX facade is introduced.

Checks precede mutation: wrong caller/grant -13, closed grant -9, nonzero reserved
RDX -22, missing/stale/terminal child -9. A denied move preserves the old owner.
The recipient cannot move it again. Bootstrap cannot reclaim the authority after
handoff, including after the recipient closes, exits, faults or is stopped.
Termination makes the binding unusable; subsequent slot reuse cannot inherit it.
No UART FIFO flush or replay is promised. Reopening/recovery and arbitrary
cross-core delegation are intentionally outside this one-hop mechanism.

Aether owns native enforcement; sys-init can later select the service and perform
handoff; userland owns console routing/terminal policy. This does not assign or
implement those companion services. New tests use conformance clients only.
The IF-clear BSP transaction serializes lookup, generation binding and ownership
change with task lifecycle. One slot/generation pair is retained until reboot;
there is no retained pointer into reclaimable task memory. Existing v1 remains
unchanged and its original suite is a required regression.

Required witnesses before acceptance: denied/terminal/stale target preserves old
access, successful move removes old access, worker cannot transfer onward, live
binary exchange in the recipient, close and fault paths, subsequent generations
denied, and wrong-input oracle rejection. Run console_smoke.py with --handoff and
--handoff-fault, plus the original mode, host checks and native channel regressions.
No shared standard, consumer pin or original test marker is changed by this step.

The generation-omission mutation must fail at supervisor 944/reclaimed 2: a new
worker must not acquire a faulted recipient's grant merely by reusing its slot.
That control uses the fault path without close, so a closed-bit check cannot hide
an absent generation check. Retain the deliberate failure and restore final
sources before the qualified suites. See STATE for the resulting evidence.

Producer validation: v1, v2-close and v2-fault modes pass on final sources, each
including wrong-input rejection. The generation-omission control fails as required.
[Evidence](evidence/native-console-handoff-2026-09-06/README.md) records scope and
all attempts. Companion adoption and production console routing remain pending.

## Composed console/channel profile v3 (pre-implementation contract)

AENSC003 / ABI 12 composes the existing AENIN001 two-image envelope, two bounded
channels, launch/paired-endpoint transfer, lifecycle and wait operations with the
v2 exclusive UART handoff. Bootstrap registers retain ABI 6's factory/image/channel/
wait grants; this explicit profile additionally supplies console selector 0xf001
with initial bootstrap ownership. No existing envelope bytes or ABI change.

This enables a separately launched console transport task to communicate with a
client using two 32-byte channels. The client receives endpoints, not UART access.
It does not assign production POSIX/TTY policy or implement sys-init. Aether owns
enforcement; companion adoption remains separate. Same BSP/IF-clear ownership,
quotas and lifecycle cleanup apply, with no new operation, allocator or dependency.

Required result: serial bytes reach the console task, cross a channel to a second
address space, return through the other channel, and reach serial output. Reject
wrong payload in that second task; deny its raw UART operations and deny UART in
a replacement console slot. Confirm bootstrap loses transferred endpoint/UART
access, both workers terminate, channels clear and three instances reclaim. Old
console modes and native init/channel regressions must pass. Update the workflow
entry and retain source-frozen target/host evidence. Run console_smoke.py --relay
with the same explicit SDK arguments. This is a transport composition, not a shell
or filesystem milestone; the production console adapter is still owner work.

V3 producer evidence now passes the real two-address-space round trip, wrong-input
rejection and an intentionally corrupted client reply. Eight console, nine init,
four channel and seven M4 cases pass on final sources. See
[retained results](evidence/native-console-relay-2026-09-06/README.md). The actual
sys-init implementation and userland terminal adapter have not adopted ABI 12.

## Console plus process-owner profile (selection, 2026-09-11)

Before connecting actual dash stdin, compose the existing UART authority with the
three-image process-owner layout. AENMX003 / ABI18 preserves AENMX002's80-byte
header, three bounded ELF images,48 entropy bytes,16KiB owner limit, one-page stack,
six channels, worker quotas and factory/image/channel grants. R9 remains the third
image grant0xc003. The initial owner additionally owns the existing console selector
0xf001, including its single exclusive handoff. There is no new operation or grant
in existing profiles. Wait authority is not implied by this new layout.

Reuse the existing console relay witness: move endpoints to separate console and
client domains, transfer UART only to the console domain, require a real binary
round trip and deny bootstrap/peer UART access. After both domains exit and reclaim,
launch the third image in the former console slot and require UART denial. Three
reclaims and exact terminal outcomes are required. Wrong input must fail at the
existing peer/owner boundary; a generation-check bypass must not pass slot reuse.
Host tests retain canonical size/framing rejection. Run all existing console modes,
full connections, five launch and both init capacity suites because loader mapping
is shared. Keep source-frozen receipts and failures; update STATE/workflow after
qualification. No sibling, SDK, released pin or ordinary boot change is selected.

SE-01–SE-05: silently granting UART to existing AENMX002 would broaden old authority.
An explicit version composes proven enforcement without adding a UART abstraction,
new service policy or kernel buffering. Reuse the existing relay to qualify this
boundary before changing shell I/O semantics. Kernel still validates each bounded
UART span and owns the slot/generation binding; userland owns terminal policy.
This is transport availability in the shell layout, not actual dash serial input,
TTY/line discipline, recovery or R1 acceptance. Empty UART remains EAGAIN, never EOF.

Preflight refinement: the real exchange and first denied reuse succeeded, then
existing connections completion rejected three reclaims (it requires six). Retain
that failed attempt. Keep the existing kernel completion gate and use four fresh
third-image generations in the former console slot, yielding six reclaims. Leave
the first recipient's grant open so close cannot mask a missing generation check.
The final oracle requires the full six-terminal inventory.

The final --connections relay envelope pads its owner to exactly16KiB to exercise
all four code pages of this explicit format; compiled relay logic remains small.
Use the standard console_smoke.py command above with --connections. Existing modes
keep their original bytes and limits. No new production terminal output is added.

Qualified result: [the composed profile](evidence/console-process-profile-2026-09-11/README.md)
passes the binary exchange, six-terminal inventory and full16KiB envelope. The
first six-reclaim attempt exhausted the existing per-slot generation cap. Final
fresh workers use slots0,1,2,0, preserving that cap and checking denied console
reuse in generations2 and3. The omitted-generation mutation rejects fresh71 /
owner941 / reclaimed2. All older console modes, connections, launch and both init
capacity suites pass. Final console-only fixture/oracle corrections were tested in
a separate frozen round; the kernel and inputs used by the other suites did not
change. Exact per-profile source differences and all attempts are retained.

## Private dash backend composition — 2026-09-11

The [serial dash experiment](NATIVE-SHELL-STARTUP.md#actual-serial-dash-composition--2026-09-11)
uses AENMX003/ABI18 without changing the kernel ABI. A separate Rust worker receives
F001 once; bootstrap, dash and its child cannot use it. The private owner channel
exposes logical handles f101/f201/f202 for stdin/stdout/stderr via the existing
32-byte read/write/close frames, maximum16 data bytes. UART EAGAIN remains EAGAIN;
the process owner retains nonempty blocking reads. Offsets are validated against
each logical stream and advance only after actual transferred bytes.

The backend serves two logical sessions within one authority lifetime. After all
three handles close, exactly one all-zero32-byte reset request reopens the logical
handles and returns their original hello frame, with positions reset. The caller
is the single authorized supervisor channel. Old clients are terminal/reclaimed
before the new session publishes references. Reset while live or after the second
session is rejected. This is a private bounded protocol, not a shared TTY API or
a general service-restart contract. The grant remains open through backend exit;
a fresh backend-image worker in that slot must receive EACCES and exit17.

The complete connections suite invokes console_smoke.run_dash_console internally
and preserves its exact QEMU command, host exchanges and serial output. The
standalone `console_smoke.py --connections` grant/slot-reuse regression remains
unchanged. No new developer entry point is added.


The [serial pipe-substitution profile](evidence/dash-pipe-serial-2026-09-13/README.md)
reuses AENMX003/ABI18 and the unchanged two-session UART backend. The connection
owner forwards exact stdio bytes and retains EAGAIN reads; actual dash executes
two substitutions at returned prompts, then a fresh shell runs a builtin command.
The backend's replacement is denied the old grant. See NATIVE-CONNECTIONS and its
existing `--connections` command. Combined exec/pipe support remains separate.

The [serial external-substitution profile](NATIVE-SHELL-STARTUP.md#serial-external-substitution--2026-09-13)
adds `/next` inside both substitutions using the same UART backend, four prompts
and clean second shell. Its `-stale`/`-grant` controls corrupt the second pipe's
exec commit/startup respectively. The existing connections invocation runs all
three; no additional command-line interface or console grant is introduced.

## Five-worker serial pipeline profile (AENMX006 / ABI20)

The separate capacity-enabled AENMX006 envelope retains AENMX005's112-byte header,
three image lengths,80 bytes of entropy and24-KiB supervisor ceiling. Bootstrap
register arguments remain the three image grants, factory and channel factory;
ABI20 additionally grants only the bootstrap owner UART selector0xf001. This is
an explicit private profile, not a new right for AENMX004/005 or ABI19 consumers.

Only v1 console read/write/close (0x26000..2) is exposed. There is no handoff in006.
Reuse existing caller, pointer/span, length, EAGAIN/short-count and permanent-close
checks. The bootstrap owner remains the authority holder across three fresh shell
lifetimes, and closes its grant after their terminal-confirmed teardown. Parent and
copied workers must be denied direct UART use. They hold scoped stdio descriptions;
stream closure does not close another holder's binding or the underlying UART.

The Rust owner synchronously forwards validated stdio frames through that grant,
retaining pipe/descriptor/wait ownership. Dash owns parsing and job construction;
no line discipline, job control, global POSIX device, or init policy is added.
The first acceptance is one real pipeline followed by a builtin/exit at returned
prompts, repeated across three shell generations. See the prospective review in
NATIVE-SHELL-STARTUP and STATE for actual qualification. Run the full
`scripts/pipeline_capacity.py` command documented there; serial positive, changed
input, bad grant and disabled006 cases are included. Existing console and serial
exec/substitution tests remain required regressions before adoption.

Serial forwarding follow-up: AENMX006 no longer retains cumulative stdout/stderr
captures or compares them to a script literal. It checks authority and frame bounds
before each synchronous UART transfer, preserves EAGAIN/short-count behavior and
checks holder closure at completion. The existing finite driver/request budgets
still apply. Per-request16-byte framing and one-byte UART transfer bounds remain;
removing a test capture does not add an unbounded queue or general TTY service.
The host now checks long stdout/stderr before a pipeline and long output afterward,
with nine prompt-driven commands over three fresh generations. Corrupted output
must fail the ordinary host oracle even when guest lifecycle cleanup succeeds.


The separate AENMX007/ABI21 lifetime profile grants no UART authority. Its owner
and workers require direct UART operations to return unsupported(-38). This does
not extend006's serial contract; a composed serial session still needs explicit
input/output and grant-lifetime qualification. See the
[session admission contract](NATIVE-SHELL-STARTUP.md#aenmx007-admission-and-channel-integration--2026-09-24).


## Selected terminal mode drain observation —2026-11-01

The default-off boolean `-Dnative-tty-mode-probe=true` adds one scalar query to
only the current private BSP ABI31 ordinary-app filesystem-owner closure. It
rejects release, SMP, mktemp-reader, Zsh application and AF09 diagnostic profiles.
Append only this option to that existing closure; no envelope, quota or grant
changes. Older profiles retain their exact operation selection, including whether
`0x26003` handoff is recognized. An unselected `0x26004` returns ENOSYS(-38)
without hardware access.

For selected int81 `0x26004`, RDI must be F001 and RSI/RDX/R10/R8/R9 must all be
zero. The existing exact live holder/recipient slot, generation, admission,
nonterminal and closed-grant rules apply before hardware. Reserved scalars return
EINVAL(-22), wrong holder/token EACCES(-13), and closed grant EBADF(-9). One COM1
line-status read returns0 only with valid TEMT(bit0x40); THRE(bit0x20) alone
returns EAGAIN(-11). All-ones status or TEMT without THRE returns EIO(-5). This
selected profile enables existing RX-error retention before every LSR poll,
including earlier byte/diagnostic writes before readiness or a drain query. The
query also enables retention before its one read, preserves pending errors and
never reads the receive-data register. Nonselected legacy monitoring stays
unchanged. The query has no pointer, allocation, queue, UART mutation or kernel
wait. Rust owns all mode policy and bounded waiting.

The fact observed is preceding UART-accepted bytes leaving the transmitter.
It does not prove remote receipt, exclusive COM1 use or native busy timing.
Deterministic tests distinguish THRE from TEMT and retain first-read RX errors;
actual image fit, native behavior and separate review remain distinct gates.

Focused host checks (Zig0.16.0, no image/guest):

```sh
zig test kernel/native_sustained.zig
zig test kernel/native_tty_mode.zig
python3 -B -m unittest discover -s tests -p test_native_tty_mode.py -v
python3 -B -m unittest discover -s tests -p test_build_policy.py -v
```

The Python check compiles the actual console operation body, verifies selected
build arguments using `zig build --help`, and requires compiling omitted-holder
and THRE-substitution controls to fail the same semantic assertions. Its host
aggregate is300 seconds, children at most180 seconds, streams4MiB and compiler
files16MiB. Owned temporary binaries/caches are removed after known cleanup.
