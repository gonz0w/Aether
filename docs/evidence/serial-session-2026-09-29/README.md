# Serial SESSION producer handoff — 2026-09-29

Producer qualification passes for the unchanged consumer workload under private
AENMX008/ABI23: three actual interactive dash parents, nine prompt-driven inputs,
27 copies,21 helper replacements,24 image admissions and30 terminal/reclaims.
Each parent produces65 stdout bytes,19 program-stderr bytes plus six prompt bytes,
and90 UART bytes. Shell variables and PID persist across prompts.

All160 capacity cases pass across matched runs:149 existing cases plus11 serial
cases. Five legacy command regressions and four explicit008 envelope/ABI controls
also pass. All132 Python/configured Zig/Rust/pin checks pass, with11 native log
comparisons and88 rejected checker mutations. Across35 linked owner variants,
maximum code/estimated stack is18856/24576 and3944/4088; the nine serial variants
use at most16400 code and3832 stack. Inspection is scoped, not a formal stack proof.
Immutable builtin targets were checked at1334 indirect call sites.

This is a producer handoff, not independent userland acceptance, reader sign-off,
shared SDK integration or assembled R1. Next: userland replays SERIAL-SESSION-01–06.
SI-07 still needs its separate versioned bootstrap/transport and rebuilt runner/
bytecount. No sibling repository or released standards pin changed.

The final source/support export and final verification are authoritative for replay.
`unqualified-proposal.patch`, `restored-runtime.json`, the packet-local initial
`serial_session.py`/test, and all probe archives are historical attempts only.
Do not use that draft patch or those initial scripts as current implementation.

Requirement before code: consume pinned SESSION-SERIAL unchanged commands in three
interactive dash parents, with prompt-driven partial input writes, exact UART and
separate stream/lifecycle observations, owner-only serial authority, stale denial
and confirmed idle-parent cancellation. Preserve15 lifetimes, three children/two
pipes,24KiB owner and4088 stack. No sibling or released standards edits.

Use explicit private AENMX008/ABI23 to compose007 session lifetimes/observations
with006 owner UART authority. Existing envelopes and ABIs remain unchanged. The
smallest sufficient change reuses the session owner/client and kernel console
primitive; silently granting UART to007 would violate compatibility. No new service,
public SDK operation, kernel policy, scratch namespace or generic TTY is added.
The owner forwards accepted bytes only after binding/rights/identity validation;
EAGAIN keeps the current request pending. All wire buffers remain synchronously
borrowed at existing unsafe traps. No arbitrary payload gains UART authority.

Host framing recognizes only exact existing kernel record grammars after the boot
boundary; every other byte belongs to UART and must match the consumer stream.
No arbitrary-line filtering, sleep handshake, future-command preload, fabricated
prompt/EOF, or timeout-as-cancellation is allowed. Match phase terminals and native
owner collection invariants at each returned prompt. Retain raw byte offsets,
prompt/generation/input events and all attempts. Upstream prompt bytes and machine
markers remain unchanged (Experience v0.1.0 existing-output exception applies).

Select bounded parser/order counterexamples, malformed envelope/legacy tests,
native authority/negative/cancellation controls, full affected capacity plus legacy
commands, host checks and linked owner code/stack inspection. Update existing
STATE/ROADMAP/interfaces/workflow with actual results and remaining owner gates.
General TTY/job control, arbitrary transport interruption, SDK and R1 remain open.

## Integration diagnosis and progress

The first selected native run failed with owner2820. Trace probe2 identified an
incorrect quiescence check on each read: interactive parsing may read while
constructing a job. The check moved to the returned prompt boundary. Probe1 was
an invalid diagnostic envelope (80-byte offset instead of112) and timed out before
owner launch; it is never counted as a semantic control. Probes3/4 exposed pipe
setup failure; probe5 echoed actual received bytes and confirmed unchanged input.
Probe6 preserved ENFILE as diagnostic parent154; probe7 recorded first/second pipe
allocations and exhaustion. Probe8 added a short diagnostic return-address write.
These diagnostic mutations are not production behavior or passing qualification.

The cause was local template selection: the scripted parent links the Linux
reference input.o, whose nonbufferable stdin path reserves a tee pipe even with
--disable-tee. Existing serial parents instead select the pinned native input.o
(`b3ba65369b2befb50009b04bbe12f95e2556030e1d4bbcaeb639ff3de379588a`),
which uses upstream's one-byte fallback. The initial provisional conclusion that
a new input contract was needed was incorrect. The existing native configuration
resolves it without quota growth, fake termios, upstream changes or sibling work.
The inspected upstream source/disassembly is explanatory and retains the original
source-authentication limitations; actual native linkage is pinned and validated.

An intermediate restoration to the previous six source files was byte-verified
and passed127 host/configured checks. `restored-runtime.json` records that temporary
checkpoint, not the final runtime. `unqualified-proposal.patch` preserves the then
unfinished implementation. The proposal was resumed with the correct native input
object. `native-input-fix.log` now records the successful three-parent positive;
`positive-sources.*` pins its runtime. All diagnostic attempts and their complete
outputs/source snapshots were archived, readback-verified and duplicate directories
removed. The matched native build is pinned by `capacity-1-sources.*`; final checker differences are reconciled in `source-version-review.json`.

## Scope and security review

The simpler alternative is reuse of006 or007 unchanged. It is insufficient:
006 lacks the accepted fifteen-lifetime session contract, while007 deliberately
has no UART grant. The explicit008 selector combines existing kernel mechanisms
and reuses one owner/client rather than adding a second transport or shell engine.
It removes no accepted compatibility path; all debug instrumentation is confined
to retained attempts. No public SDK or reusable TTY framework is introduced.

Untrusted shell processes hold generation-bound stdio references and authenticated
owner channels, not UART capability. Copied processes and replacements probe
foreign UART read/close denial. Invalid references fail before hardware access;
owner checks buffer/record capacity before writing the UART. EAGAIN keeps a request
pending, and positive short progress is returned exactly once. The fixed caller
stack buffers are borrowed synchronously only across existing trap boundaries;
no pointer is retained. Lifetimes, two pipe objects, three children and code/stack
bounds remain unchanged. Phase quiescence is checked on the actual returned prompt.
Cancellation requires a real empty read after phase1 collection, an authenticated
stop of the exact parent, a terminal observation and confirmed reclaim. It is not
UART unplug or EOF detection. Larger programs, terminal editing/job control,
signal recovery, concurrency exploration, reader review and shared SDK remain gaps.

The read allowlist is parent-only for this workload; helpers receive inherited
stdio bindings but actual helper reads use the pipeline. The four environment
entries remain PWD=/work, WITNESS=value, LC_ALL=C, PATH=/nonexistent; UID1000 and
upstream default PS1/PS2 supply `$ ` and `> ` without widening the environment ABI.
No command echo is enabled. Kernel diagnostics can interleave physical UART, but
the host removes only exact specified marker grammars and retains every raw byte.
Separate fd1/fd2 observations are checked in addition to the combined UART stream.

## Exact controls and attempts

| Case | Owner result / reclaims | Required outcome |
| --- | --- | --- |
| composed, stale-wait, stale-reference |100 /30| Three healthy parents; stale ECHILD preserves status; stale serial reference returns EACCES |
| wrong-env |2800 /2| Helper91, parent31; empty stdout and first prompt only |
| bad-byte |100 /30| Actual UART `pipe` becomes `PiPe` in both pipelines; logical stdout remains original; normal oracle rejects |
| bad-substitution |2801 /6| Parent33 after18 stdout/four prompt bytes; all five children exit0 |
| fd-leak |2802 /10| Helper95, parent35 after44 stdout/six prompt bytes |
| wrong-grant |2891 /1| Wrong UART selector EACCES, no forwarded bytes/input, exact parent stop143 |
| cancel |2890 /5| Phase1 finishes, second prompt appears, no second command; real EAGAIN, parent stop143 and four healthy children |
| stderr-error |2892 /10| Retired stderr rejects diagnostic; dash continues through session ok;65 stdout/six prompt bytes, wrapper141 |
| stderr-route |100 /30| Diagnostic actually uses stdout binding:84 stdout/six prompt bytes; UART remains90 and ordinary per-stream oracle rejects |

The all-case run completed149 legacy plus two serial cases before an incorrect host
expectation for the corruption control stopped it. Both p characters change;
expecting `Pipe` was wrong. The first serial-only rerun completed nine cases, then
showed that stderr retirement still permits final session ok before wrapper141.
The final serial-only run passes all11 on identical native payload inputs. The
host checker was strengthened to bind exact admission identities and each parent's
observation after all its terminals and before the next parent admission. The
missing-admission test already rejected; the early-observation test initially
failed and now passes. Failed runs and test logs remain alongside final evidence.

## Commands and replay

Run `python3 scripts/pipeline_capacity.py --libc-build <pinned-sdk> --tools-lock
<pinned-tools.json>` for all160 cases, or add `--case serial-session-composed` for
the positive. Run `python3 -m unittest discover -s tests -p test_serial_session.py
-v` for the five host tests; `zig build test` includes them and the existing checks.
The packet's serial-controls/envelope-controls drivers retain exact build commands
and payload/source bindings; their original zig-out paths are recoverable from the
verified artifact archives. They are evidence reproduction tools, not release CLI.
`oracle-controls.py <final-serial-output-directory>` performs the11 raw comparisons
and88 mutation controls. `export-replay.py` constructs a complete local source/
support export and verifies an isolated host replay; native replay additionally
requires the recorded pinned SDK, tools and firmware. No mutable sibling is followed
by the build. Native input configuration remains separately pinned in the source.

Host input is fragmented into requests of at most seven bytes with each actual
os.write return recorded; this does not claim every OS call itself returns short.
The owner returns real one-byte UART progress against larger bounded requests.
All raw serial offsets, event generations, accepted input counts and emulator
reaping receipts are retained. No timeout qualifies a semantic negative.
