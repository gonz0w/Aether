# C file-client transport evidence — 2026-10-21

UL-007/081/082: the [opt-in transport](../../proposals/FS-FD-CLIENT.md) now sends
AEFD0001 requests through trusted C callbacks, handles short I/O and would-block
waits, validates whole replies and retires once on unknown/malformed completion.
It borrows one caller-owned4096-byte workspace and releases its pointer after
clearing on abort. Both raw close results remain visible; no replay or reconnect.

Actual Python3.10.21/3.14.7 each pass1631 scripted host schedules and seven compiling
semantic omissions. C17 strict warnings, nonmutating format and UBSan pass. Exact
previous C requests/Rust replies are replayed; this experiment does not invoke live
Rust, native traps or OpenZFS. Source-only input has nine members, manifest seal
`eac972b501518c97f67d483aafe6186ea2b5863dfaad26930108d4d7d290c48c` at
`build/service-deliveries/filesystem-fd-client-2026-10-21-v1`.

Schedules exercise all64 short chunk widths, every832-byte reply/704-byte request
interruption prefix,16 corruptions, nine callback-failure modes, local denials,
full4096-byte reads at last sequence, semantic-error continuation, maximum255-byte
components and initialization preconditions. Counts group some assertions into
one schedule; they are not native task counts. A complete conversation compares
all emitted bytes to the prior actual C request stream and independently checks
ab/cd/f data, results/status, sequence, padding and zero unused output. No reply
metadata changes on a rejected/incomplete request. Controls require exact assertion
text for sequence, wait failure, budget, body validation, retirement, clearing and
local shape omissions; compiler failure/UBSan/timeout is not their success oracle.

The checker pins full immutable v3 and prior evidence manifests before reading
inputs, including the previous archive. Actual request/reply fixtures have original
hashes; their once-only extraction provenance is retained in inputs/. Source,
checker, compiler/formatter, LLVM resource headers,105-header host SDK closure,
UBSan runtime and owned process helper are recorded before consumption. Header/
source/runtime pins are rechecked. Each process uses clean PATH/LC_ALL/TMPDIR,
60s compile/30s test limits and16MiB streams with explicit cleanup receipts.
No binary reproducibility comparison is claimed across private build paths.

Attempts retained: initial formatting-sensitive body-mutation target mismatch;
passing1628-schedule predecessor; passing1631-schedule storage-lifetime correction;
minimum Python missing optional lzma before compilation; final minimum/current
runs using hash-pinned plain704/832-byte fixtures. The optional xz issue introduced
no new tool dependency or target-code workaround. Exact checkers and all logs,
mutation sources/binaries, source snapshots and inputs are recoverable from the
verified retention archive; root names/byte accounting appear in retention.json.
No old accepted candidate, wire, native limit, standard/SDK pin or sibling changed.

The [review](review.md), summary.json, candidate.json, final-source.json, raw quality
streams and SHA256SUMS record scope and identity. The local quality gate verifies
standards/documentation structure, not independent review or runtime readiness.
Original wire/process dependency evidence is reused only for unchanged source and
its stated host/native-object scope. There is no new native object/link/fit/runtime
qualification, libc facade selection, complete shell/dispatcher or immutable exec.

Next: reviewed file/pipe/console FD routing and shell startup selection, exact native
copy/failed-exec parent/FD preservation, immutable executable admission, whole native
workspace/code/stack/heap/backing/channel fit, matching sys-init dispatcher and
Aether native command/error/cleanup/fresh boot. C callers must serialize and prevent
reentrancy; callback deadlines/authentication/lifecycle remain trusted obligations.
Independent owner/reader review and full UL-007/081/082/M3/R1 remain incomplete.
