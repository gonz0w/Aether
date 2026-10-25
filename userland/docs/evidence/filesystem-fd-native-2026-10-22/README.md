# Native descriptor adapter batch — 2026-10-22

UL-007/081/082; [contract](../../proposals/FS-FD-NATIVE.md), [pre-code review](review.md),
[observations](summary.json), [candidate](candidate.json). This batch supplies
concrete native-call channel/stream/pipe/guard adapters without selecting a new
startup/greeting format or linked shell. Source labels require authenticated owner
admission. Existing service, wire, C session/redirection and prior deliveries are
unchanged. No sibling edits/messages, native guest, installation, pin/default/quota
change, monitoring or cross-project acceptance.

Final actual Python3.10.21 and3.14.7 runs each pass193 host native-call scenarios,
482 existing C/Rust cases (269 file+213 redirection),88 prior host scenarios per
child and four new/eight retained compiling semantic omissions. New coverage:
all32 request prefixes and32 reply prefixes, chunk widths1..16, EAGAIN/wait,
attempt exhaustion, oversized native counts, malformed reserved/payload bytes,
private errno bounds, admission/rights denial, both pipe objects/generations1..9,
reused generation/collision, every pipe reply byte corrupted, exhaustion, unknown
close, cached raw close errors, reentry, guard rejection and restoration failure.

Session-level tests exercise actual host pipe bytes/EOF, alias-aware physical
close, complete pipe pair publication, nondestructive cloexec projection and
terminal finish. A write with no reply reaches an actual host pipe once while the
client reports unknown and refuses replay. Restoration failure exits a real host
child125 via the injected backend after both channel closes. All native calls,
source control responses and source authority in this host adapter fixture are
injected; this is not a native syscall/dispatcher/mask/pipe enforcement witness.
The separate482-case suite executes the unchanged Rust handler/process/AF07 service
with synthetic storage. Its previous192 lost file-reply prefixes remain covered.

Strict C17/format/UBSan and Rust2021/rustfmt/default Clippy/unsafe checks pass.
All166 host headers,217 exact prior native headers, tool/resource/runtime/helper
pins are checked before use and rechecked afterward. `vendor-pins.json` binds the
verbatim existing native trap header; supplemental llvm-objdump is pinned before
inspection. Eleven freestanding ELF64/x86-64 objects relocatably link with only
memcmp/memcpy/memmove/memset unresolved. Actual backend disassembly contains int81.
Fifty-nine static frame reports/max264 bytes exclude callbacks/call chains/libc/
interrupts and full workspace/heap/backing/channel fit. No executable, loader,
Aether execution or native enforcement claim follows from these objects.

The48-member source-only handoff is
`build/service-deliveries/filesystem-fd-native-2026-10-22-v1`, manifest SHA256
`5cfc0b125564fd9e3dc0e9319c5495f63dbe5f651154af61bf7393b2f1dbdc33`.
It carries exact prior source bytes plus native adapter/backend/tests/trap header,
checker snapshot, contract, license and dependency/vendor receipts. The checker
snapshot expects the maintained repository layout; reproduce using the commands
in the contract, not by executing the snapshot from its delivery directory. No
SDK, engine, executable or linked shell is delivered here.

[Retention](retention.json) and [driver](retention-driver.py) inventory four owned
qualification attempts in attempts.tar.xz: one checker count mismatch after all
initial191 adapter scenarios passed, one complete191 pass and final193 minimum/
current passes. Test strengthening did not change production code. Every source,
checker, command/environment/deadline, stream, child cleanup receipt and build
artifact is retained. Streaming hash/size readback of every regular member occurs
before exact root removal. Setup/documentation dispositions are in summary.json.
Retention removed40,763,703 logical bytes from the four attempt roots and kept
7,499,984 archive bytes. Logical accounting is not physical disk reclamation. Retention
uses current Python/lzma separately from minimum qualification. Quality and final
source/input preservation receipts accompany this packet.

Implementing-agent technical review only; independent owner/reader pending. Native
wait has no wall-time deadline: owner stop/watchdog and actual settlement remain
mandatory. Sys-init Decision0199 now consumes session/redirection on host; it still
requires a coherent linked shell/startup, one greeting consumer, actual identity/
binding/history/factory/copy/immutable executable/failed-or-unknown-exec parent/FD
preservation, complete resource fit and matching dispatcher/readiness/shutdown,
then fresh Aether commands/errors/cleanup/readback. No POSIX/SIGPIPE/job-control/
full M3/R1/TTY/Zsh/package acceptance is claimed. Existing full shell remains open.

Final quality gate passes, including all three pinned standards checks and draft
coverage validation. Minimum/current syntax, git diff --check and scoped new-source
whitespace pass. [Verification](verification.json) and verification.tar.xz retain
the final owned commands with complete cleanup; its temporary root was removed
only after streaming readback. Thirteen predecessor source deliveries, four prior
evidence packets and the217 native headers verify unchanged. No independent
review is inferred from these checks.
