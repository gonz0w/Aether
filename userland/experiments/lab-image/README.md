# Offline lab-image experiment — UL-007 / UL-012

build.py supplies the maintained path from a sealed session SDK candidate to a
bounded x86-64 UEFI VM kit. It rebuilds the parent/helper, requires their whole ELF
hashes to match the qualified AENMX008/ABI23 or AENMX009/ABI24 payload, then inspects every actual
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

The ABI24 profile selects [one-parent boot instructions](BOOT-ABI24.md). The
externally selected input profile must match both envelope magic and rebuilt SDK
profile. It consumes a qualified wait kernel, lifecycle owner and wait-aware
clients; the old ABI23 kit remains valid within its polling limit. See
[ABI24 qualification](../../docs/evidence/session-channel-wait-consumer-2026-10-03/README.md).

## Check a delivered ABI24 kit

boot.py supplies a fresh prompt-driven VM check of a clean sealed ABI24 kit. Select
its SHA256SUMS digest from the delivery evidence before invocation; a newly computed
hash alone does not establish trusted source selection. For the independently
qualified repaired sys-init kit:

```sh
python3 -B experiments/lab-image/boot.py \
  --kit build/lab-kits/sysinit-rebuilt-abi24-2026-10-04 \
  --kit-seal 43456fed1202884302296575ba55107ad183281322c0e075505bba446d80c6ff \
  --output build/my-lab-boot --delay 35
```

Use a new output path for each run. The command verifies the exact kit namespace,
regular bounded files, selected hashes, ABI24 successful-build receipt, ISO/firmware
bindings, qualified command bytes and exact QEMU binary before starting a guest.
Only the clean builder inventory, receipt.json and optional OWNER.md are supported;
older kits with incidental test outputs reject. ABI23 is outside this check.
Metadata/hashes confer no native authority and are not signatures or a build audit.
Selected kit data is inert; no kit hooks or Python/shell scripts execute.

The guest uses single-CPU TCG, fresh variables, no NIC and the recorded QEMU11.1.1
profile. It receives three supplied commands only after exact prompts and prior
phase cleanup. The maintained serial oracle checks90 UART bytes, eight admissions,
ten terminal/reclaims and owner-authorized halt. --delay 35 waits35 seconds at the
first prompt and two seconds later; default 0 uses immediate fragmented input.
This fixed workload is not an interactive launcher or an unrestricted shell test.

Python3.10+ on the qualified macOS POSIX host. Guest90s, driver105s; UART1MiB,
QEMU stderr4MiB, outer output16MiB each. The unchanged owned process helper owns
the driver group; QEMU inherits it and is explicitly terminated/killed/reaped.
Timeout, panic, wrong bytes/identities, incomplete cleanup or missing tools fail.
Control-C/host crash/detached hostile children are outside this scoped qualification.
No network, real-prefix installation, physical-media writes or background monitor.

Help/version/results use stdout, errors use escaped plain ASCII stderr. Exit0
means the exact boot workload passed; usage64, missing input2 and operational1.
Success prints only the absolute output path. receipt.json schema
`aether-lab-boot-v1` retains selected kit seal, source/interpreter/QEMU identities,
delay, owned-process receipt and status incomplete/failed/pass. session.json and
serial.log retain native events, exact UART and independent oracle result. The
session/ directory holds fresh flash and QEMU stderr; native.* holds driver output
and cleanup receipts. These are experiment records, not a published native ABI.

On failure, preserve the output and inspect receipt.json, session.json, serial.log
and native.stderr. Recheck the selected kit/tool identity and choose a new output
for another run; never alter a sealed kit to hide failure. Successful boot is
separate from SDK/owner acceptance, physical hardware, full TTY/storage/packages,
recovery and release. SSDK-06 reader review remains deferred.

Host controls (13 kit denials/eight CLI contracts/four trace corruptions):

```sh
python3 -B experiments/lab-image/test-boot.py --kit KIT --kit-seal SHA256 \
  --output build/boot-host-tests
```

[Maintained-command evidence](../../docs/evidence/lab-boot-command-2026-10-04/README.md)
records actual minimum/current interpreter tests and fresh native boots. Historical
oracles/packets and all earlier kit archives remain immutable.

The [source-rebuilt owner intake](../../docs/evidence/sysinit-recipe-consumer-2026-10-04/README.md)
now consumes sys-init's frozen maintained recipe on minimum/current Python,
rebuilds exact owner/client bytes and independently boots the new matched kit.
Earlier sealed kits remain unchanged and valid in their qualified scopes.
