# Toybox image bounded usage rejection

Pre-code contract, 2026-09-07. The selected native cat profile accepts stdin only.
Reject any extra argument before toy_singleinit/cat_main, using real public musl
fprintf/fflush and the established ASCII usage line/status64. This is the private
profile adapter, not upstream Toybox help or option support. Validate copied
startup and AECAT001 first. No input request, stdout byte, mask initialization,
Toybox allocation or applet/callback execution may occur on rejection.

Flush diagnostics while aliases are live; consume all three even after EIO/EINTR
or unknown completion. Preserve64 through diagnostic/close failures. Shared poison
must prevent further channel calls; closing aliases locally does not claim remote
closure, which remains owner-supervised. Same binary retains actual cat for no
extra arguments. No kernel/owner/SDK/pin/sibling or quota change is planned.

Select -, -u, -v, filename, --help, --version, unknown option and empty argument;
short diagnostic writes; EIO/EINTR and malformed/cut diagnostic replies; known
close error; no memory grant; normalcopy. Four intentional read/corrupt/status/
close mutants must reject at1520/1505/1501/1503. Run prior actual error/cat suites,
full command regressions and host/Zig/pin/workflow/format. Freeze sources, retain
failed attempts before edits. Foundations O/I/E, Experience output preservation,
DEVELOPMENT and unchanged upstream licensing apply. Update STATE/NATIVE-CAT/workflow.
Finalizer failure/re-entry and independent CAT acceptance remain later work.

## Native cases

| Cases | Required result |
| --- | --- |
| copy |Actual no-argument cat still copies binary input and exits0 |
| dash/unbuffered/format/file/help/version/unknown/empty |Extra argument rejects64 with all37 usage bytes, no input request or stdout bytes |
| short |Same complete usage under native three-byte writes |
| diagnostic-eio / diagnostic-eintr |Owner confirms16 diagnostic bytes, then error;64 retained, no retry, all aliases consumed |
| diagnostic-malformed / diagnostic-cut |First16 diagnostic bytes may commit without confirmation;64 retained, no later channel traps, owner-supervised remote cleanup |
| close-eio |Complete usage, known consumed input-close error, remaining cleanup and64 preserved |
| no-memory |Same rejection with the client memory grant withheld; no Toybox initialization |
| read-input / corrupt / force-zero / skip-close |Exact owner1520/1505/1501/1503 rejection; no generic panic accepted |

The same image contains real Toybox but the rejection adapter intentionally runs
before its initialization. Assertions require zero mask-call, Toybox allocation,
configured-buffer, callback, flush-observer and Toybox command state. They do not
claim all libc internals perform no allocation; the no-memory native case proves
this bounded message succeeds without an anonymous-memory grant. Real fprintf
may partially deliver a diagnostic before failure; status64 never claims delivery
or remote close success. Shared transport poison and independent owner cleanup
remain authoritative. Usage cases reuse the retained owner images. The ordinary
command owner correction discovered during regression is described below; kernel
and installed SDK behavior are unchanged.

## Regression failure and scoped correction contract

Full command attempt1 failed bootstrap-early-publication: child97 then owner990,
missing parent69/owner970. This is a product failure in the fixture owner's
lifecycle/channel observation, not accepted negative coverage or an infrastructure
retry. Exact sources, recipe, commands and outputs are retained in
command-attempt-1-artifacts.tar.gz with separate results/log/timing records.

Before correction: a running lifecycle poll can become stale before channel read.
Kernel finish closes channels and retains terminal state before rescheduling.
On EOF, recheck the same holder-scoped child handle; only a confirmed terminal
record permits returning to the existing terminal validation/cleanup path.
Still-live EOF retains existing rejection/partial-frame semantics. No fabricated
completion, ignored status, new authority, retries of I/O or unbounded wait.
A test-only bounded interleaving waits for child termination after the initial
running poll, then reads EOF; a mutant bypasses revalidation and must reject990.
Existing early-publication oracle remains child97/parent69/owner970. Full command
suite gains both controls; rerun native usage/errors/cat, host and full command
on final frozen sources. Owner Rust uses rustfmt1.98.0 edition2024; no mass format.
Update command contract and evidence; installed SDK, kernel, pins and siblings
remain unchanged. The existing per-generation200000 bound also bounds the test
interleaving. Extra lifecycle queries allocate nothing and retain generation scope.

Command attempt2 was intentionally interrupted after review found the first
interleaving control could be bypassed by an already-terminal initial poll. This
is incomplete test coverage, not a product pass or timeout. Its exact sources and
partial outputs are retained in command-attempt-2-artifacts.tar.gz. Correction:
once per generation, the control models a stale running observation even when
termination has already won the initial poll, waits boundedly for actual retained
termination, then reads EOF. Normal builds never override a lifecycle observation.
This closes the schedule-dependent test gap without changing the runtime fix.


## Final qualification

Native attempt3 passes all20 usage/copy cases; prior actual error11 and cat7 suites
pass. Command attempt3 passes all213 cases, including the original early-publication
oracle, the forced stale-poll control and its exact990 bypass mutant. All98 host
tests, Zig tests, immutable pins, workflow36 groups, Rust1.98.0 edition2024 and
Clang-format21.1.8 checks pass. Full command run took673.4 seconds within the
1800-second review ceiling. Host/format timestamps were not recorded separately.
Native attempts1/2 also passed, but their pre-correction source inventories do not
qualify the final command-owner revision; attempt3 is authoritative.

Four final receipts match frozen runtime sources. Compared with the preceding
Toybox-error milestone, only toybox-cat-probe.c, owner.rs and launch_smoke.py changed.
SDK libc/receipt/tool-lock and every immutable UL-059 bundle artifact are unchanged.
No kernel ABI, grant, quota, installed SDK, release pin or sibling repository changed.
Default cat ELF is85,952 bytes,22 load pages,4-byte TLS. These are artifact measures,
not peak memory, throughput or assembled-release evidence.

qualification.json and the four *-results.json files bind final inputs/outcomes.
final-artifacts.tar.gz retains sources/, run-native.py and all four output trees;
archive-check.json records verified source/recipe identity. Both earlier command
archives retain exact source/recipe bytes and raw partial outputs, with separate
*-results.json, logs and timing. Attempt1 is a product failure; attempt2 is an
intentional interruption for a test-design gap. Neither is counted as a pass.
ISO, installed boot duplicates and kernel.elf are omitted from archives; artifact
hashes remain in receipts. Prior source/third-party notices are retained.

Reproduce with run-native.py and the exact invocations in errors/cat/command-timing.json;
run `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global` for
host checks. The full command suite covers the changed ordinary-command owner;
the Toybox suites retain their independent cat owner images. Other kernel/native
profiles and isolated stdio/startup suites were not rerun because their runtime
inputs are unchanged. Missing independent consumer review, extended testing and
assembled R1 coverage remain open.

**Next:** callback-produced buffered output, flush/close failure and finalizer
re-entry coverage, then independent CAT consumer acceptance. This gate does not
implement Toybox options/help, persistent storage, a shell or package installation.
The accepted full R1 roadmap remains unchanged.
