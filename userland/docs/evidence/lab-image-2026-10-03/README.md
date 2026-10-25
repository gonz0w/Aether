# Offline lab-image experiment — UL-007 / UL-012

build.py supplies the maintained path from a sealed session SDK candidate to a
bounded x86-64 UEFI VM kit. It rebuilds the parent/helper, requires their whole ELF
hashes to match the qualified AENMX008/ABI23 payload, then inspects every actual
ISO boot component before copying the ISO and fresh firmware templates. It never
changes kernel/owner code, grants, image formats or sys-init/package policy.

```sh
python3 -B experiments/lab-image/build.py --help
python3 -B experiments/lab-image/build.py --inputs build/lab-inputs \
  --input-seal SELECTED_SHA256 --output build/lab-kit
```

An externally selected lab-inputs.json digest pins the exact boot file inventory,
tool identities and SDK seal. The source directory contains image/, firmware/, licenses/ and
bundle/. Boot files are regular inputs; links, stale/missing files and wrong
profiles reject. The complete SDK seal is verified before its trusted build
support executes. This is source selection, not a sandbox against hostile build
code or concurrently mutated inputs. Output must be new and under build/.

receipt.json distinguishes incomplete/failed/pass builds; clients/ and iso-check/
retain compiler/inspection outputs, full command receipts and cleanup. kit/ is
published only after exact client and ISO closure checks. No build invokes QEMU
or writes real media. [Boot instructions](BOOT.md) define the bounded workload.

Python3.10+; standard library, exact Clang/LLD recipe and pinned xorriso required.
Help/version stdout0; invalid usage stderr64; missing inputs stderr2; operational
failure stderr1; success prints only the kit path on stdout. Diagnostics escape
control characters and are plain ASCII. No interactive confirmation or background
monitoring. A failed partial output is retained; choose a new output for another
attempt. Current evidence is [lab qualification](../../docs/evidence/lab-image-2026-10-03/README.md).

All quality, Experience, standards, distribution, syntax and whitespace checks
pass. The transfer kit has15members with full readback; its exact
archive digest is in delivery.json. All1747work files and1link metadata
were archived/read back before only this redundant work root was removed,
reclaiming61177856allocated build bytes. The final kit remains under build/lab-kits/.
For cold rebuild, safely unpack lab-inputs.tar.gz to a new build/ directory, select
the exact input_seal in cold-inputs.json and run the maintained builder with a new
output. Pinned tool paths must match; changing the lab host requires new explicit
tool selection and qualification. Restore the recovery archive to its original
path to replay the dated check/smoke drivers.
