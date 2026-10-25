# 0214: Fresh matching AF07 input chain and guarded-owner diagnostic

2026-10-23 / BG-070 / UL-007/081/082. This is offline preparation and local
implementation review, not independent acceptance or a native pass.

Root [review](../../../docs/reviews/2026-10-23-af07-inputs.md) records requirement,
security, simplicity, forbidden outcomes and focused checks. Root STATE owns
system integration. Current engine/activation selection is the explicit private
`docs/native-af07-inputs-v1.json` at the system root; released pins and historical
seals remain unchanged. Active dependencies live under root `.deps`, not evidence.
Recompile from current sources rather than modifying an old manifest or accepting
stale live-source pins. Actual enforcing loader and size/stack checks still apply.

Correction to0213: SESSION excludes storage-lifetime. Its actual kernel frame r9
is c003 (immutable image), not e002. Explicit event operations separately use e002.
The ABI31 consumer again requires c003. A new root test compiles the actual kernel
frame expression and feeds all eight scalars into the real Rust validator; wrong
scalars, e002 and old ABI30 rejection are checked. Prior synthetic-frame testing
missed this defect; previous evidence stays intact. No VM used the incorrect check.
No unsafe site, grant, kernel ABI or resource limit is added.

The separate component harness is `scripts/qualify-af07-owner.py`. From the system
root, inspect the selected candidate without launching a guest:

```
python3 -B sys-init/scripts/qualify-af07-owner.py --inputs .deps/fs-owner-af07-2026-10-23-v1 --seal db1a489dd2117482502791a143cb911f2a570973263c17140b93ea07eed6d158
```

Add `--prepare` to build two selected images. Preparation verifies the complete
source/tool/runtime/artifact chain, real ELF/raw/envelope admission and fixed
budgets, then removes copied sources, SDKs and intermediate objects. Only the two
pending qualification ISOs and their preparation receipt survive. The independent
reader validates original pinned objects and its runtime closure before/after
building and before every guest. The reader has only a READ block grant.

After a fresh human disposition under OPENZFS-FEASIBILITY's changed-composition
rule, use `--run --prepared OWNED_DIRECTORY --prepared-sha256 RECEIPT_SHA256`.
This is exactly pristine original-file reader, guarded-owner writer, then a fresh
original-file reader only after clean writer success. No retry. Host watchdogs
remain60/30 seconds and guest ceilings6000/3000 ticks;35MiB, seven domains, twelve
channels,49152 code,8192 stack/data and64KiB normalized capture remain fixed.
The fixed serial script prints AF07-BEGIN, runs `/inputs/helper status`, prints
its actual collected exit7 and exits. It issues no filesystem mutation request;
import/export may write metadata. Existing9-mutation/96-request qualification
remains separate. This tests bootstrap/copy/immutable exec/wait/shutdown, not Zsh,
persistent executable loading, writable shell paths or general process recovery.

Qualification requires exact admissions/terminal identities and ordering, helper
status, all21 cleanup rows, bounded halt, clean engine terminal and fresh complete
original-file/media recovery. Panic, unknown result, partial output or timeout
stops the sequence and records human disposition required. Emulator stop must be
confirmed independently of guest success; unknown stop retains its resources.
After a confirmed stop, compact results survive and generated media/images are
removed. Plain internal help/version/JSON and escaped stderr use0/1/64 exits.

Checks from this component:

```
python3 -B -m unittest discover -s tests -p test_harness_af07_owner.py -v
python3 -B scripts/check-quality-process.py
python3 -B scripts/check-static.py
```

Six focused methods cover actual intake/parser, resealed altered bounds/closure,
all omitted/duplicated writer records, prepared-receipt identity and first-failure
sequence stops, plus real host-process serial fragments, panic, EOF, watchdog and
confirmed reap. These host doubles do not establish native behavior. Fresh native
qualification, failure/continued-parent cases, independent acceptance and R1 remain.
