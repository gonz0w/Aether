# SDK consumer link preparation — UL-005

probe.c deliberately exercises only header selection, object generation and static
libc linking through strlen. It has no C process startup or native adapter. Never
execute the ELF as a host binary or claim this entry is a complete native program.

[Pre-import evidence](../../docs/evidence/sdk-consumer-preimport-2026-09-07/README.md)
uses an isolated copy of the verified owner candidate payload. Strict C17,
-nostdinc, empty sysroot, -nostdlib and explicit libc.a select only that SDK.
Missing headers and omitted libc fail with named diagnostics and no output.
ELF inspection requires x86-64 ELF64, no undefined symbols or dynamic interpreter.

The captured one-shot driver records exact tools, argv/environment, inputs and
owned-process receipts under build/. It is preparation, not a supported package
command. Once pkg-mgr returns the real imported SDK and package pins, first verify
them, then adapt this driver to that exact source root and rerun. Do not call an
unregistered candidate an imported package. Full SDK-05 additionally needs chosen
startup/adapter closure and compiler-helper failure controls; SDK-07/08 retain
static rebuild and native execution gates.

## Imported package checkpoint

[Imported-SDK evidence](../../docs/evidence/sdk-imported-consumer-2026-09-07/README.md)
now verifies the real owner bundle and imported/recovered roots, then repeats
these link controls using the imported payload. The package record and descriptor
are bound to the consumer result. This supersedes the earlier pending-import
status for this leaf-function test only; full startup/adapter/helper and native
acceptance remain open.

## Startup and adapter checkpoint

[Startup-link evidence](../../docs/evidence/sdk-startup-link-2026-09-07/README.md)
rebuilds receipt-pinned io_probe.c and I/O/memory adapters against the imported
SDK with C17 and explicit crt1/crti/crtn after libc-receipt identity and source
hash checks. Helper and omitted-crt1/io/memory-path failures are recorded. This
is host ELF evidence. Later SDK-07/08 checkpoints are scoped separately below.

## Static input tracking checkpoint

[SDK-07 local experiment](../../docs/evidence/sdk-static-rebuild-2026-09-07/README.md)
adds an unused archive member in a private copy. The old input binding becomes
stale even though a fresh relink yields identical ELF bytes. Both input sets and
relink/check commands are retained. This proves the local invalidation distinction;
it does not implement package updates or qualify the modified archive on Aether.

## SDK-08 closure selection

[Selection](../../docs/SDK-08-CLOSURE.md) pins the imported-SDK io_probe consumer
and retains the historical missing-snapshot decision. The subsequent
[matched native witness](../../docs/evidence/sdk08-matched-2026-09-07/README.md)
verified the retained producer and passed bounded success/denial cases. The closure
checker validates the historical selection only; it is not the current acceptance
gate. See the [SDK review packet](../../docs/quality/SDK-REVIEW.md) for pending review,
package integration and denial-reclaim limits.

## Startup copied-source verification

The [current plan](STARTUP-PLAN.md) adds receipt-hash checks of the staged probe
and adapters before compilation. Run from the repository root with Python 3.10+
(the current run is qualified only on the interpreter recorded in evidence):

```sh
python3 -B experiments/sdk-consumer/test-startup-copy.py
python3 -B experiments/sdk-consumer/check-startup.py
```

The control changes copied bytes while preserving the live source hash and requires
rejection before any process starts. The prior harness fails that control.
[Evidence](../../docs/evidence/sdk-copy-check-2026-09-07/README.md) retains both
results and the complete link rerun. The copied-source checks assume the private
work directory remains owned and unmodified after validation.

## Prerequisite receipt failures

The startup harness retains an incomplete summary and error when prerequisite
receipt files are missing or contain malformed JSON. Verify this with
`python3 -B experiments/sdk-consumer/test-startup-receipts.py` from the repository
root. The three controls launch no compiler and retain their summaries under
build/. [Evidence](../../docs/evidence/sdk-receipt-failures-2026-09-07/README.md)
and the [plan](RECEIPT-FAILURE-PLAN.md) record that earlier scope. Consumed-field validation is now covered below;
evidence-storage failure handling is now covered below.

## Consumed receipt fields

The startup checker validates the objects, digest formats and paths it consumes
before SDK copying or tool execution. Inventory paths must be canonical relative
`stage/usr/` paths; tool/import roots must be absolute. Unknown owner metadata
is allowed. These checks do not redefine the owner's full receipt schema or
authenticate its contents. The package layout is also hashed in the run's inputs.

Run `python3 -B experiments/sdk-consumer/test-startup-schema.py` from the repository
root. [Plan](SCHEMA-PLAN.md) and
[evidence](../../docs/evidence/sdk-schema-2026-09-07/README.md) record 24 invalid
input scenarios, six libc controls, allowed unknown metadata and unchanged linked
ELF bytes. Receipt byte/depth bounds and duplicate-key checks are covered below;
hostile filesystem concurrency remains outside this local validation scope.

## Complete local preflight review scope

Receipts are UTF-8 JSON capped at 2 MiB and 64 container levels. Duplicate keys
and nonfinite JSON constants reject. Quoted structural characters do not count
toward nesting. These are local consumer limits, not a changed package format.
Evidence-storage failures return 1 with an explicit stderr error; the checker does
not claim retention when it cannot create/write the summary. Existing files remain.

Run `python3 -B experiments/sdk-consumer/test-startup-preflight.py` alongside the
three earlier startup control scripts. The [plan](PREFLIGHT-PLAN.md) and
[evidence](../../docs/evidence/sdk-preflight-2026-09-07/README.md) retain the initial
nesting-control failure and corrected rerun. Byte limits do not establish an RSS
limit or total execution deadline; private staging and trusted filesystem assumptions
remain. The [SDK review packet](../../docs/quality/SDK-REVIEW.md) now includes this
completed local preflight slice for independent review.
