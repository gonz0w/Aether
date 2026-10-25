# 0210: Route the actual mixed process channel under one owner admission

2026-10-22 / BG-070. Pre-code review.

The linked shell sends64-byte AEFD0001 file messages,304-byte AEFORK01 fork
snapshots and32-byte stream/pipe/wait messages over the same authenticated process
channel. Existing Peer::serve_one consumes64 bytes before classification, while
fork capture must close admission before reading its first16 bytes. They cannot
be connected by reading a prefix outside the gate or reopening between prefix
classification and full fork validation. This is a current integration defect,
not a reason to add another channel, queue, descriptor ledger or protocol.

Add one owner routing admission which closes before the first read. A completed
ordinary exchange may reopen only with an active source. A validated fork reserves
its actual nonzero increasing sequence and leaves the same owner Capturing.
Read/parse errors stay closed; unknown source effects retire as before. Host unwind
stays closed. The callback cannot reenter or retain mutable owner/source borrows.

The router uses the sole authenticated Peer/channel and caller4096 workspace.
Read exactly16 first; exact AEFD0001 continues to64 and the unchanged real FILE
handler/body/reply logic. Exact AEFORK01 continues to304 and the unchanged full
fork decoder, identity/generation/reserved/flags/source/history checks. The
remaining selected32-byte stream/pipe/wait shapes go to an explicit required
owner callback; no default successful handler or invented exec selector. Unknown
magic/opcode or malformed first header rejects before any body/handler effect.
Reuse workspace for the two nonoverlapping304-byte fork buffers and clear it on
all returns/host unwind. Header stays a bounded64-byte local, no automatic4KiB.

Peer gains an externally received-header entry sharing its existing validated
FILE exchange, and a scoped channel borrow for the trusted router. Neither API
authenticates a new peer or changes its Process/generation. Preserve old serve_one,
wire/error/close behavior and sealed deliveries. Input labels never supply native
authority. New routing is a local opt-in consumer, not an old owner replacement.

Test actual FILE handler/ledger/AF07 fixture with a mixed scripted byte channel:
open/read/flags then captured fork, source offsets/flags and queued mutation denial;
short/EAGAIN, every prefix truncation, malformed/unknown header, replay/wrong peer,
same physical channel and no extra greeting; stream callback under admission;
partial reply/source retirement/once-only source+peer cleanup and unwind clearing.
Compile semantic gate/prefix omissions, strict host/native Rust, relevant existing
peer regressions, and compare actual composed routing code/frame observations.
No guest until the full native owner/entry/lifetime/shutdown fits and is admitted.

All existing code/stack/data/backing/channel/worker/watchdog and9/96 bounds remain.
This safe Rust change adds no dependency or unsafe boundary; raw native ownership,
copy/refusal/readiness/terminal/reclaim and immutable exec remain separate explicit
owner obligations. The current linked input remains dash foundation, not Zsh.

Simplicity: directly join the existing handlers under one exclusive admission,
sharing their validated exchange implementation. Independent entry wrappers cannot
resolve prefix ownership/order. This removes duplicate header ownership and the
need for a second channel or framing cache; no generic router framework or new
protocol. Whole-owner integration and peak stack remain open, not external waits.
Implementation-agent review; independent and native acceptance pending.

Before the operational loop, handle an idle peer without parking the whole owner:
the first nonblocking <=16-byte read is inside the gate; EAGAIN with zero consumed
bytes completes no work and reopens. After any consumed prefix, finish boundedly
under the same gate; never discard a partial frame as idle. The owner can scan
other peers and then use its existing observe/park sequence to avoid missed wakeups.
Test idle parent followed by active copied child, no wait/source effect on idle,
and interrupted partial headers. Partial-client stalling still consumes the fixed
poll/watchdog bounds and can stop this POC owner; per-client availability/isolation
is not claimed. Ordinary FILE body/reply retains its existing per-frame Framed
bound; the new caller budget covers mixed prefix/fork/stream transport, not an
invented common wall-clock deadline. All watchdog/resource limits remain fixed.

Code-fit comparison after routing correctness: use the same pinned compiler,
libraries, source and fixed bounds for bounded link-only probes of safe identical
code folding and disabled jump tables, individually and together. Safe ICF must
preserve address-significant functions; no all-functions ICF or changed identity
contract. Disabling jump tables retains the same checks/control flow semantics.
These add no runtime dependency, authority or larger budget. Reuse host tests by
exact input identity, record each target artifact/flags/size and do not adopt a
flag from size alone or claim optimized native execution. If they do not improve
fit, retain the existing build and report the shortfall. Full owner/call graph and
native tests remain required; no source validation may be removed to gain bytes.

After safe-ICF/no-jump probes leave the core above budget, one further bounded
link-only comparison may select the pinned LLVM machine outliner (`always`,
reported by this compiler's own hidden help), alone and with no jump tables.
This may replace repeated instructions with helper calls, so inspect emitted
helpers/call frames and do not treat a smaller fixed subtraction as peak-stack
proof. There is no new hand-written runtime or dependency. Keep the default
unchanged unless complete-owner resources and native behavior are qualified;
unsupported flags/build failure stop that probe rather than masking its result.
