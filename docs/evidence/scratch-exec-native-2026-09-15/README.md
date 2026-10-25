# Native scratch image replacement — 2026-09-15

The opt-in scratch_exec witness copies the actual C process with a live writer,
then replaces that child through native prepare/query/commit. FD3 survives;
CLOEXEC FD4 and FD10 are removed by the validated files plan. The new image starts
with fresh adapter state, receives the existing stream bootstrap, validates the
child scratch root/table/description, and uses the restoration helper before I/O.
Child stream references use the existing explicit rebind convention; the original
bootstrap parser and all older grant formats are unchanged.

The old image's staging call cannot return success. The replacement checks that
both CLOEXEC aliases are absent before creating a new stdin alias for the original
stream fixture. Its writer resumes after pre-copy A and writes B/C. The owner
independently verifies ABC, closes its readback description, and observes both
lifetimes finishing source71/child72/backend17 with six reclaims. This is actual
native replacement with private staging, not public execve or unchanged dash.

## Results

- Three focused cases pass on attempt3. Keeping the unfiltered descriptor table or
  supplying the old parent file reference produces child254 and owner1950 with
  zero reclaims. Exact terminal sequences are independently recorded in traces.
- All338 connections cases pass in1051.059935seconds, below the1800second review
  ceiling. Outer suite timeout3600seconds and per-case bounds remain unchanged.
- Host Zig/offline checks and104 Python tests pass; C/Rust formatting, workflow
  and the simplicity manifest/four-member verification pass.
- Positive owner15320bytes; controls15336/15352bytes; all clients ELF25856bytes.
  All fit existing limits. No kernel change or increased worker/memory quota.
- The prior643 compiled ELF/raw images compare byte-for-byte unchanged.

## Attempts and retained evidence

`focus-1.log`, attempt1 sources and artifacts retain a compile failure: exec_fds
was not enabled for the new selection and a32-byte helper was called on a128-byte
bootstrap. Attempt2 fixes both but rejects the replacement at client254 because
its stream bootstrap changed the reference prefix expected by the old parser.
Attempt3 preserves that parser and follows the existing pipe replacement's child
rebinding pattern after validation. Both failures are retained, not overwritten.

`attempt-3-sources.json/tar.gz` freeze278 runtime/support inputs for the focused
and full successful runs. The other attempt manifests/archive pairs preserve
their own exact inputs. `connections.json` records command, timestamps, result and
source recheck. Suite results/artifacts retain SDK/tools/build/VM provenance.
`focus-selection.py` selects the three unchanged harness cases for focused runs;
`run-full.py` records the full command. These scripts are retained evidence, not
new developer entry points; replay to fresh output paths. Host commands are the
existing `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.

Every artifact archive has a complete file-hash inventory. The collector verifies
all members and rehashes loose originals before removing only exact duplicate
suite directories. Per-attempt cleanup receipts record paths/counts/bytes. Prior
sealed evidence remains unchanged. SHA256SUMS seals the final packet.

## Remaining work

This plan removes aliases but intentionally retains the writer holder. Native
last-description CLOEXEC release and denied-exec retention with live files are
next. Then unchanged dash fd-leak-control/redirection, full connections and a
matching full runner before independent SDK/consumer acceptance. Poisoned scratch
close and confirmed-stop recovery, persistent filesystem and R1 assembly remain
open. No public API adoption, sibling modification, released-pin change or full
interactive-shell readiness is claimed.
