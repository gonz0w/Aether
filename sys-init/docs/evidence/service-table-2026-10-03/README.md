# ABI22 inert service table — 2026-10-03

BG-067; [decision](../../decisions/0179-abi22-inert-service-table.md),
[guide](../../AETHER-BASELINE.md). This is an explicit developer composition,
not a published standard, descriptor interface or complete init product.

One constant data table binds Backend/image1/order0, Runner/image0/order1 and
Command/image2/order2. All automatic retry counts are zero. Constant evaluation
checks exact role/image/order membership and rejects unsupported policy. Owner
selection and native image-slot lookup consume the table; the existing ABI entry,
grants, paired owner and protocol admission remain enforcement boundaries.
Completed command reuse/finite epochs are distinct from failure retry. Only this
topology is currently valid; a cosmetic edit cannot enable a new runtime policy.

The explicit --service-table build skips sustained::begin and its old 3005-tick
idle/denial probe. The default compile path retains it. Both paths preserve the
same native ABI, userland payloads, protocol assertions, ownership/cleanup and
boot markers. Fatal fixture errors and fixed-output assertions remain test policy;
this does not claim all test machinery has become product behavior.

## Reproduction and native acceptance

Commands from /Users/cam/DEV/sys-init on recorded macOS arm64 tools:

```sh
python3 scripts/build-aether-baseline.py out/service-table-normal \
  --dependencies out/si07-loop/.deps --service-table --smoke
python3 scripts/build-aether-baseline.py out/service-table-baseline-compat \
  --dependencies out/si07-loop/.deps
python3 /tmp/service-table-early-halt.py
python3 -m unittest discover -s tests -p 'test_harness_aether_baseline.py'
```

The early-halt driver is retained at early-halt/driver.py; it verifies the normal
ISO and firmware inputs before reusing that exact image in a new private guest.
Each guest uses private variables, TCG, one core,256MiB,no NIC,90-second deadline,
4MiB serial bound and owned process-group shutdown. Local trusted tools are not
sandboxed by the recipe. Hashes establish bytes, not signer authority or complete
library/sysroot closure. ISOs stay in the named out/ roots, with hashes here.

normal/ passes one actual bytecount cycle: exact ordered terminal statuses0/0/17,
one completion, three reclaims and authorized halt, ticks9,idle0. early-halt/
passes halt before the first command, ticks1,idle0,zero terminals/completions/
reclaims. Neither trace contains SI07 idle-ready. These are two bounded VM
observations, not a boot-time performance benchmark or full wait/race matrix.

baseline-compat/ rebuilds owner.raw, owner.elf and native-c.bin byte-for-byte
identical to the prior qualified default baseline. No unchanged native workload
was rerun merely to increase counts. The table image has separately pinned raw/
ELF bytes,9,984-byte code within16KiB, and scoped inspected stack2,712 within4,088
usable. intake/ retains exact candidate compile argv/tool/source hashes, linked
assembly, raw/ELF, inspector and indirect-call review. All eleven indirect calls
resolve through immutable memcpy/memset pointers, including the two rbx calls.
The conservative inspection is not formal whole-program or kernel-stack proof.
The final recipe requires raw/ELF equality with that inspected candidate before
building or booting. The experimental recipe lock binds both profiles and current
source identities; shared release bytes/pins are unchanged.

## Controls and review

Ten focused tests pass. The new compiler test includes a valid constant table and
five semantic controls: image mismatch, duplicate/wrong role, unsupported order,
nonzero retry and missing member. Each requires its expected compiler diagnostic
and no output artifact; unrelated compiler/tool failure cannot satisfy the oracle.
Existing archive/path/identity/output-preservation/error/CLI controls remain.
The aggregate validation receipt is retained separately after all local checks.

The simpler alternative was scattered documented constants; it did not bind the
new owner and image mapping to one checked definition. Choosing a static table
avoids a parser/generator, generic dependency graph, package activation layer or
runtime allocation. The table removes duplicated role/slot policy in this explicit
profile and the startup test delay. Existing paired ownership is reused. No ABI16
service-pair mechanism is imported into ABI22. No new unsafe/FFI operation, external
dependency or sibling mutation is introduced. Sources/ retains changed owner
modules, reused owners/helper, builder, tests and the consumed lock.

Foundations O-01–05/I-01–06/E-01–08, Distribution scoped service/release clauses and
Experience output/marker preservation apply. The SV candidate is not implemented
by this local constant data representation. This is local technical review, not
independent sign-off. Bounded failure replacement/retry exhaustion, useful usable
environment composition, remaining SI-07 negatives and assembled v1 are still open.
Next implement bounded supervision on this path without replaying unknown effects.
