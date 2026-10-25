# Real generic AES native component

2026-10-04, R1-03 CPU-profile qualification. Unchanged OpenZFS2.4.4 generic AES source
from commit71a9f9578616a90c3c14bb59629fb4d31bfd68d1. Complete prior31-file/1979-member
provider packet and19-file/5037-member original-source packet verify before selecting
regular SDK/headers/source. No sibling/pin/ABI/kernel/quota/default-image changes.
[Contract](contract.md) records authority, bounds, negative oracles and limitations.

Five first-attempt cases pass: qemu64/max positive, encryption241/decryption242
mutations and frozen-time244. Both contexts exercise actual generic key-schedule,
encrypt/decrypt callbacks for128/192/256 bits, independent expected ciphertext and
independent ciphertext decryption, in-place operations, input/schedule immutability
and surrounding canaries. Work remains correct across at least four advancing
virtual timer ticks, with at least64 repetitions of all three sizes per context.
The ceiling is100000 repetitions. All existing memory/TLS/64-yield/output/terminal
checks remain. Controls reject at exact ordered terminal/panic checks, not timeout.
Public vector bytes come from [FIPS197 (2001), AppendixC](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197.pdf).
NIST archives this edition and states the2023 update does not change the algorithm.
[vectors.json](vectors.json) records the independently reviewed constants/source.
This is component correctness evidence, not FIPS validation or cryptographic certification.

Actual compiled generic object disassembly covers770 decoded sites and contains
no AVX/AVX512, AES-NI, XSAVE/XRSTOR or XGETBV instructions. This audit is scoped to
that object; probe/libc/full-engine dispatch is not certified by it. The generic
algorithm has secret-indexed tables: successful tests do not imply constant-time
behavior, side-channel resistance or production encrypted-pool approval. All keys
here are public vectors and are never runtime entropy. Accelerated AES/GCM, other
algorithms, tunables and actual initialized-engine dispatch remain unqualified.
Timer progress witnesses the workload spans interrupts, not every instruction.

Only a real component runs, through its exported generic operations object. No
fake dispatch initialization, generic algorithm replacement, engine startup, pool
or volume access. The ordinary27-page fixture fits; this is not full-engine admission.
Remaining engine prerequisites are real providers/configuration/identity/entropy,
rebuilt checked callers, selected feature closure and measured owner-local memory/
thread limits. Current8-MiB/two-child/four-admission profile does not fit the measured
host engine. Those are local work, not an external SDK or new companion blocker.

Private evidence recipe, fresh owned root with recorded current tools/runtime:

```sh
python3 docs/evidence/openzfs-native-aes-2026-10-04/setup.py
python3 docs/evidence/openzfs-native-aes-2026-10-04/native.py
python3 docs/evidence/openzfs-native-aes-2026-10-04/audit.py
python3 docs/evidence/openzfs-native-aes-2026-10-04/checks.py
```

Receipts bind complete source seals/readback, actual commands/times, compiler and
execution tools/headers/SDK/runtime, ELF/ISO/serial hashes and frozen-input checks.
No failed setup/build/target attempts occur; semantic mutations are successful
negative controls. QEMU retains its30-second external watchdog; max changes only
the helper CPU literal. Full133-Python host suite plus Zig/Rust/pins/workflow,
scoped C/Python/simplicity/local links pass before retention. All attempts and
new artifacts are read back before owned cleanup. Reused SDK/header copies are
verified against their retained original archive members and omitted from the new
archive to avoid redundant storage; immutable prior packets stay available.
Upstream source/notices retain CDDL/public-domain terms; new wrappers/recipes are
BSD-2-Clause. No owner sign-off or filesystem/release gate closure follows.
