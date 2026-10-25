# ABI22 partial reply and cleanup qualification — 2026-10-03

Four fresh native cases pass without a maintained runtime change. The existing
transfer accumulator accepts fragmented replies only when complete. An incomplete
reply after a backend write rejects instead of replaying the request or proceeding
to successful halt. Real cleanup errors leave the owner Unknown with outstanding
ownership recorded and cleanup/stop/start replay denied.

| Private image | Oracle | Code bytes | Inspected stack |
| --- | --- | ---: | ---: |
| split | Limit actual backend reply reads to16 bytes; original transfer accumulator assembles32; one useful cycle and three reclaims, buffered halt | 10640 | 2776 |
| lost | Actual backend write reply prefix reports two bytes accepted; deliberately close reply reader before remainder; assertion952, no next request/completion/halt | 10864 | 2776 |
| close | After actual command/runner terminals and protocol settlement, externally close runner reply reader; cleanup sees actual EACCES13, retains Unknown reader/worker, denies replay; assertion1406 | 10072 | 2808 |
| reclaim | Externally reclaim terminal runner; cleanup closes endpoints then gets actual EBADF9, retains Unknown worker identity, denies replay; assertion1406 | 10056 | 2808 |

The lost case exercises a consumed reply prefix, not a fabricated success/error
value. It is a deliberately induced ownership/transport loss after a write
acknowledgment prefix, not evidence of spontaneous kernel ambiguity or durable
storage. The backend-issued marker never recurs after reader loss. Failure cases
retain one request-ready prompt and no command-complete or authorized-halt marker,
even with h buffered behind r. Cleanup cases require exact command/runner terminal
order and release-call counts2/3; no further native close/reclaim calls follow
rejected replay. These cases intentionally stop at a fatal fixture assertion;
they do not claim recovered cleanup, continued service or orderly shutdown.

## Test construction and limits

The preceding sealed request-loop source archive is the base. Its complete seal
and copied dependency hashes verify before staging; source-overrides.json names
all changed files and the exact base archive. Per-case source/ retains every
changed file. Maintained runtime stays unchanged. Private visibility changes let
test instrumentation report exact boundaries. The original backend exchange and
transfer accumulation remain in use: the split/lost image caps actual read sizes,
and the lost image closes the borrowed reader after the write prefix. A first
unexecuted layout used two separate transfers; it was replaced before any guest
run so the actual original accumulator is exercised. A read-loss candidate was
also replaced before execution with write-loss to cover an already accepted effect.
Their build records remain explicitly unaccepted under unexecuted-*.

Private end instrumentation names952/1406 before the existing fatal marker; any
other assertion fails the native oracle. Cleanup probes disturb ownership only
after real observed terminals, check the exact Unknown/resources/errno result,
then follow the original failing unwrap to end1406. They do not introduce an
alternative production error handler. Existing host owner tests and prior native
Unknown-guard omission controls remain applicable; these four cases qualify the
sustained command context. They do not prove every syscall/race/failure schedule.

All images fit unchanged16384-byte code and4088-byte usable stack bounds. Linked
control-flow inspection includes fatal paths; immutable RIP-relative builtin
bindings are resolved from raw bytes. The two register calls per image use RBX
loaded from memset: split0x401457/cell0x402988; lost0x401506/cell0x402a68;
close/reclaim0x4013b2 with cells0x402750/0x402740. No intervening RBX write exists
before either call, and memset preserves callee-saved RBX. All other indirect calls
resolve to memcpy/memset; no indirect jumps. This is a scoped inspection aid, not
formal verification, kernel-stack coverage or performance evidence.

Commands, native oracles, exact source deltas, raw/ELF/envelope bytes, ISO identities
and logs are retained; ISO/firmware stay private under out. Reconstruct a source
stage from the pinned preceding archive and this case's overrides. Source snapshots
are checked after each execution. No sibling reads/writes, released pin changes,
new dependency, or other-platform campaign is involved. Native runs all passed
on their first execution; unexecuted build candidates are not passing witnesses.

Simplicity review: no runtime abstraction is needed because the existing small
primitives satisfy these tested failure requirements. Keep test-only routing and
assertion instrumentation out of maintained runtime. Nothing else is removed;
legacy images and prior packets remain historical evidence. Applicable O-04,
I-03–06 and E-01–08 require retained uncertainty, no effect replay and exact evidence.
Existing Experience internal ASCII marker scope and Distribution developer-console
limits apply; no new exception or complete conformance claim is made.

Next BG-067 work is a concise SI-07 acceptance disposition and v1 integration plan:
separate satisfied command-loop requirements from remaining wait-transition,
useful-session, service restart/configuration and assembled-image requirements.
Do not turn these known fixture failures into a claim of production recovery.
Independent review and release acceptance remain separate. All ten local gates pass in run-9e5aifkj with checked sources unchanged.
validation.json and validation/ retain the report; git diff --check passes.
sha256.json seals all files except itself.
