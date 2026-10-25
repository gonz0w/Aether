# Native engine profile and admission reconciliation

2026-10-05,R1-03. Offline producer review; no runtime, ABI, quota, SDK, sibling
or released pin change. [Contract](contract.md) records the scope before tooling.

The actual guarded native startup ELF contains the **baseline** libzpool queue
objects. Exact object/link receipts route its guarded partial object through the
original177-object baseline aggregate, including original taskq/ARC/file objects.
Separately compiled1/1 system/delay, serial ARC and one-worker file-vdev trial
objects never entered that aggregate. The baseline retains64+4 system workers,
automatic ARC eviction and MAX(boot_ncpus,16) file workers. The reduced host
trial's82-worker observation cannot establish this different ELF's fit.

All44 retained host sample records reconcile. Ten measured one-CPU/serial-file
samples each report82 live created workers and281 lifetime creates; main is
additional. These are historical Linux observations, not fresh native engine
runs or counts from this ELF. The82-child native service limit includes helpers;
the primary context is separate. One additional reaper would require at least83
child records for that observed population. A test creator counts separately only
if it does not replace an engine worker. Production helper placement and actual
native engine peak remain undecided.

The current native loader reparses the exact4,371,768-byte guarded startup ELF:
four load segments,4-byte ELF TLS and1309 initial pages including the64-KiB primary
stack. Ordinary limits reject; large layout passes; W+X and oversized TLS controls
reject. This is fresh host parser evidence, not admission or execution. The actual
sealed repeated-service client/ELF receipt separately binds its66-page per-pthread
mapping observation. Those TLS, guard and allocator costs cannot be substituted
for the engine's unmeasured native allocation costs.

| Hypothetical additional helpers | Total children | Fits82 slots | Image plus66-page fixture mappings | Remaining from8192 pages |
| ---: | ---: | :---: | ---: | ---: |
| 0 | 82 | Yes | 6721 pages | 1471 pages /6,025,216 bytes |
| 1 | 83 | No | 6787 pages | 1405 pages /5,754,880 bytes |
| 2 | 84 | No | 6853 pages | 1339 pages /5,484,544 bytes |

The worksheet excludes engine heap/ARC and additional runtime/provider state.
Its zero-helper row does not establish progress with a blocked primary. Available
grant pages are not reserved engine memory; even positive arithmetic is no native
fit proof. Do not turn the table into a product quota. The512 lifetime ceiling is
separate from live records and must include actual helper creates;322 synthetic
admissions do not replay281 engine creates.

Nine exact counterexamples reject profile substitution, lifetime-as-live counts,
invented measured heap, unsupported admission, omitted helpers, excess live slots,
false page headroom, hypothetical engine fit and independent-peak substitution.
Full137 host/pin/workflow checks, scoped Python/Zig/links/whitespace and simplicity
snapshot verify separately. No unrelated target regression is claimed.

Setup attempt1 stopped at the newer pin packet's `kind` field after verifying
three prior packets; older receipts used `type`. Selected files, source, error
log and partial receipt remain. Attempt2 recognizes the exact recorded schemas
and verifies selected manifests and every archive member before analysis, without
extracting or following historical links. Analysis inputs/tools remain frozen.
Two documentation patch submissions failed framing/context before writes; scoped
retries change documentation only, not qualified analysis inputs.

Next rebuild a deliberately selected native engine profile from original objects
and reviewed queue policy, without host observer callbacks or suppressed provider
failures. Qualify actual helper progress/counts and measure native heap/ARC/TLS
before selecting enforcement limits. Scoped resources/identity/configuration,
feature closure and calibrated monotonic/UTC precede engine startup/fini/restart,
granted-volume/Rust filesystem/package composition and assembled R1. Public SDK/
reader and independent consumers remain separate. Local work remains available;
no new external blocker or owner approval is established.

Private evidence recipes are not supported developer commands. Replay copied
setup.py, analyze.py and geometry.zig using fresh owned output constants; keep all
attempts. Run setup, analysis, then the existing
`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global` command.
Exact input selections, tool hashes, argv/times, geometry logs, analysis and failed
bytes remain in artifacts.tar.gz. Archive readback precedes removal of only this
review's owned duplicate output. CDDL/MIT notices accompany selected OpenZFS/musl
material; original tooling and geometry are BSD-2-Clause.
