# Concrete owner composition —2026-10-22

Scope: BG-070 / UL-007/081/082, host and target-link evidence only. No guest or ISO.
[Pre-code/design/boundary review](../../../sys-init/docs/decisions/0212-complete-native-owner.md)
records the maintainer's replacement of16KiB optimization with complete measurement.

The concrete ABI30 entry/control/owner now composes AF07 provisioning/greeting,
initial process launch, FILE/fork/pipe/console routing, retained Pending frames,
actual native copy/refusal publication, waits/terminal/settlement and checked
export/EOF/EPIPE/close/reclaim/serial/halt ordering. A failed run cannot be restarted.
The linked entry is a development measurement, never an admitted old-profile image.
Immutable exec and initial readiness are still missing. Unknown/preflight/exhaustion
fail-stop is not graceful parked-parent recovery; full copy glue scheduling and
all native authority/permissions/fault/cleanup/independent witnesses remain open.

Final selected offline image:34560 immutable RX code bytes/nine pages, no writable
image statics or unresolved symbols. One Runtime3376+workspace4096=7472/8192,
leaving720 resident bytes. Current conservative direct-edge stack6360 exceeds4088
usable: the checker exits2, status `blocked-owner-stack`, with host checks passing.
It retains the longest path, including per-function conservative128-byte margin;
this is not an observed overflow or a formal stack proof. Disabling target jump
tables for the new composition permits inspection. Immutable RIP-relative linkage
edges resolve from actual FF15/FF25 instruction/pointer bytes and exact defined
symbols in RX file-backed memory; writable aliases (including BSS), unknown,
register/table and recursive edges reject. Existing profile flags/pins stay exact.

A separate8KiB guarded RW/NX stack is proposed, pending human disposition. It would
use one extra page from the same128-page owner backing; no implementation/admission
or other limit change is claimed. The final code budget with headroom waits for a
complete exec/readiness owner measurement. Historical16KiB gates remain historical
profiles, not the new task's optimization target.

Validation:

- Producer37 in-place tests/15 semantic controls; client13/nine controls. Callback
  sees a validated disconnect ack before either close; unsettled views reject;
  failure and raw close results persist once, without replay.
- Consuming57 tests/eight strictly compiling semantic omissions/two borrow
  denials; actual FILE/pipe/codec cores with injected native/storage outcomes.
  Runtime immediate-exit lifecycle tests cover bad ack, missing EOF/EPIPE, failed
  close, failed launch, shared provisioning poll exhaustion and no second run.
  Full real-runtime copy/wait/exec schedules and native behavior are not inferred.
- Default33 process/eight remote/nine FILE-wire regressions pass. New immutable
  linkage-edge mutations and the existing unknown/dynamic/recursive/stack-limit
  regression pass. Target Runtime/control Clippy, strict builds and changed Rust
  formatting pass. Current sys-init aggregate and local workflow/userland quality
  results are retained separately; all nine current stages pass after the recorded
  inventory-count/indent corrections. Four no-preparation CLI stream/exit checks
  and both corresponding Experience pins pass; no historical native-bundle replay is claimed.

Commands from system root (use each actual printed producer directory):

```sh
python3 -B userland/experiments/filesystem-service/check-process-descriptors.py --in-place
python3 -B sys-init/scripts/check-broker-init.py --libraries PRINTED_OWNED_OUTPUT --compact-compare --unified-route --compose-owner
python3 -B userland/experiments/filesystem-service/check-client.py
python3 -B userland/experiments/filesystem-service/check-process-descriptors.py
python3 -B userland/experiments/filesystem-service/check-remote-descriptors.py
python3 -B userland/experiments/filesystem-service/check-fd-protocol.py
python3 -B -m unittest discover -s tests -p test_owner_stack_constants.py -v
PYTHONPATH=tests python3 -B -m unittest test_fs_session_init.InitOwner.test_stack_inspector_rejects_dynamic_unknown_recursive_and_excess_edges -v
python3 -B sys-init/scripts/check-all.py --current
python3 -B userland/docs/quality/check.py
python3 -B scripts/check_workflow.py
```

Every attempt is retained in compact JSON, including failed strict builds, typo/
mock EOF/epoch oracles, target-only Mach-O correction, mutant/original dependency
collision, and the rejected source-freeze run caused by a comment edit during
qualification. The latter is not a pass; final sources were frozen for the final
run. Interim links34992/default and35072/direct were observations, not approvals;
actual lifetime boundaries reduce the bound7352 to6360. A root-only no-jump probe
still had dependency jump tables and did not qualify. Initial constant-test segment
mutation used the memory-size offset instead of file-size; repair was test-only.
The aggregate first rejected its obsolete22-record assertion after three reviewed
unsafe files were added; the first assertion update introduced an indent error,
then was corrected and rechecked. No failed result is silently promoted.

`owner.json`, `producer.json` and `client.json` retain final receipts with tools,
source/target-library hashes and exact commands. `attempts.json` deduplicates
command templates: replace `${OUTPUT}` with each recorded absolute repository
root+attempt path; no command is executed from this record. Short failures and
result hashes remain, not binary/source/SDK/image bundles. `checks.json` records
focused/aggregate results. Disposal removes owned generated roots only; pinned
current dependencies and sealed inputs remain. This cannot reproduce disposed
bytes or satisfy immutable release/independent acceptance. Source/boundary review
is by the implementation agent; independent reader/owner review is pending.
