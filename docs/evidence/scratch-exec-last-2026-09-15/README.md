# Last-description close and denied-exec retention — 2026-09-15

The native scratch exec fixture now opens a separate child-owned CLOEXEC reader,
reads A, and includes its single binding4 alias in the frozen snapshot. Successful
image preparation/query precedes closing this reader's last holder; backend close
must acknowledge before image commit. The replacement cannot read the removed FD5.
Its writer remains live, continues at the shared offset, and independent owner
readback must be ABC before complete backend closure and six reclaims.

The denial variant first attempts an unauthorized image. It requires EACCES,
an unchanged empty staged-image query and the still-frozen original process.
It resumes that image without closing either file. The client checks exact local
flags/counts/references, reader EOF position and writer access, then resubmits the
same table under freeze sequence2. Only the successful retry releases the reader.
This is private native staging, not public execve or unchanged dash acceptance.

## Results

Six focused cases pass on final attempt4. Last-close and denial/retry positives
both finish source71/child72/backend17 across two generations with six reclaims.
Skip-close rejects owner2507; closing the writer instead yields child254/owner1950;
closing the reader during denial rejects owner2510; a wrong denial code yields
child251/owner1950. All controls have zero reclaims and exact terminal/result
checks. Timeouts are not accepted rejection evidence.

All344 connections cases pass in1086.478689seconds, below the1800second review
ceiling. The outer suite timeout is3600seconds and per-case bounds are unchanged.
All104 Python host tests and required Zig/offline checks pass. Formatting,
workflow and the simplicity manifest/four-member verification pass. Of649 prior
ELF/raw images compared,639 are identical; ten scratch images change from the
shared gateway and staging failure cleanup and pass their complete regressions.
Positive owners are13912/14888bytes and client ELFs26056/26504bytes. All controls
also fit existing limits; no kernel operation, worker quota or memory-limit change.

## Retained attempts

1. Four-page link overflow. Consolidating repeated generic scratch gateway calls
   into one shared function removes duplicate code while retaining all validation.
2. Three last-description cases pass. This intermediate source set is retained.
3. Added denial cases: positive and premature-close pass, but wrong-error control
   fails the execution-context oracle with child79 instead of251. Its return path
   failed to restore the mask, obscuring the intended rejection.
4. Error exits now restore the saved mask and poison before returning; all six
   focused cases pass. The full suite uses these exact final sources.

Each attempt has a frozen source manifest/archive and complete build/run artifact
inventory/archive. The final set has278 runtime/support inputs. `connections.json`
records command, timestamps, return code and source recheck; results and traces
retain exact per-case details and SDK/toolchain provenance. `host.log` and
`checks.json` retain local checks. `source-delta.json` lists the four modified
runtime/support inputs relative to the prior exec packet.

`focus-selection.py` selects the final six cases from the existing harness without
changing their implementations or oracles. Attempts1/2 selected only the three
last-close cases. `run-full.py` and `collect.py` record full-run and collection
procedures. These are sealed evidence, not new developer entry points; replay to
fresh output directories. The host command remains `zig build test --cache-dir
.zig-cache --global-cache-dir .zig-cache/global`.

Every archive member is verified against its inventory and loose originals are
rehashed before removing only the exact duplicate directory. Cleanup receipts
retain paths, file counts and bytes for every attempt. No previous sealed evidence
is edited. SHA256SUMS seals this packet.

## Remaining integration

Connect the file lifecycle to the actual dash fork/exec dispatch path and run
unchanged fd-leak-control/redirection. Full connections and a matching full runner
remain required before independent SDK/consumer acceptance. General poisoned-close
recovery, persistent filesystem and R1 assembly remain open. The closed reader in
this selection is child-owned; a description with a surviving parent holder still
has separate host ownership coverage, not a new native exec claim here. Sibling
repositories and released pins are unchanged. No full-shell readiness is claimed.
