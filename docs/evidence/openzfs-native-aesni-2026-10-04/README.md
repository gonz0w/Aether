# AES-NI and real OpenZFS AES dispatcher

2026-10-04, R1-03. Actual upstream OpenZFS2.4.4 AES callbacks, dispatcher and assembly
from commit71a9f9578616a90c3c14bb59629fb4d31bfd68d1. [Contract](contract.md) records
requirements before each scope extension. No kernel/ABI/quota, SDK/release pin,
normal image or sibling change. This is selected AES profile evidence, not full
engine initialization, a filesystem or release acceptance.

Five direct AES-NI cases pass: max known-answer positive, qemu64 unsupported238,
corrupted encryption241/decryption242 and frozen-time244. Real AES instructions
execute only after upstream is_supported accepts the CPU. No AVX/XSAVE is enabled.
Both contexts check128/192/256 key schedules, independent encryption/decryption,
in-place buffers, immutable inputs/schedules and canaries across four advancing
virtual ticks. At least64 repetitions, ceiling100000; existing TLS/memory/64-yield/
output/terminal checks remain. Vector bytes match the sealed prior generic packet;
[vectors.json](vectors.json) records their independently reviewed primary origin.

The real aes_impl_init and public key/block functions then pass a fresh13-case
matrix: default qemu64/max, explicit generic both, AES-NI max, cycling both, baseline
AES-NI denial238, pre-initialization assertion125, corrupted241/242, frozen244 and
real guard overread #PF142. Default chooses genuine x86 callbacks on qemu64 and
AES-NI on max. Cycling visits all actually supported implementations. Empty/unknown/
overlong names reject-EINVAL without changing selection. Selection is private
user-space policy, not native capability authority.

Exact16/24/32-byte keys and16-byte blocks immediately precede a PROT_NONE page;
all valid accesses pass. Misaligned in-place block buffers/canaries pass. Three
explicitly granted pages are mapped/protected/unmapped; available-page count must
restore exactly. A deliberate one-byte-past-key read produces two native faults,
vector14 and terminal kind2/detail142, before the profile panic. Existing kernel
termination/zeroing handles the deliberate faults. This is bounded FFI coverage,
not general fuzzing, all allocation failure schedules or every-instruction preemption.

Attempts: direct1 passes; dispatcher1 compile fails at upstream int/size_t comparison
under-Wextra/-Werror; dispatcher2 strict link rejects missing atomic_swap_32.
Dispatcher3 links the real upstream atomic.c and passes12 cases. Dispatcher4 adds
buffer boundaries and passes13. Every attempt, source/recipe snapshot, command,
start/end UTC, actual ELF/ISO/serial output and classification is retained. The
upstream dispatcher alone omits-Wextra, retaining-Wall/-Werror; its loop is bounded
by three immutable entries. The previously qualified fatal assertion source uses
its prior warning profile. New original C/other crypto keep the stronger diagnostics.
No assertion is disabled; the exact125 pre-init control proves it remains fatal.

Actual C/assembly/atomic/diagnostic object audit covers5613 decoded sites,
requires AES key/encrypt/decrypt instructions and rejects extended-state or privileged
instructions. No whole-engine dispatch, all CPU requirements, constant-time/security
certification or encrypted-pool approval follows. Generic/x86 table implementations
still need side-channel review; AES-NI availability alone is not crypto admission.
GCM/authentication, other algorithms, real providers and full-engine budgets remain.
Ordinary dispatcher admission36/128 pages is not full engine resource fit.

Complete provider/original-source seals and all1979+5037 members verify; the sealed
startup diagnostic input's322 members also verify. The prior generic vector packet
manifest is checked. Additional selections and a complete setup replay bind all
source/header/SDK bytes. Compiler/runtime/tool snapshots stay frozen during each
qualified run. No historical link is followed and no sibling recipe executes.

Private evidence reproduction uses a fresh owned output root:

```sh
python3 docs/evidence/openzfs-native-aesni-2026-10-04/setup.py
python3 docs/evidence/openzfs-native-aesni-2026-10-04/native.py
python3 docs/evidence/openzfs-native-aesni-2026-10-04/audit.py
python3 docs/evidence/openzfs-native-aesni-2026-10-04/dispatcher.py
python3 docs/evidence/openzfs-native-aesni-2026-10-04/dispatcher-audit.py
python3 docs/evidence/openzfs-native-aesni-2026-10-04/checks.py
```

Source identities and assembly calling conventions are unchanged. Function/data
sections plus linker GC remove uncalled allocation APIs, not unresolved reachable
imports or CPU checks. The actual upstream atomic implementation resolves selection
state; no successful no-op is substituted. QEMU retains its30-second watchdog.
Full host/pins/workflow, scoped C/Python/simplicity/source identity/links precede
retention. All new members read back; reused SDK/header copies verify against
retained original members before only owned duplicates are removed.

Licensing: CDDL engine C; [Gladman notice](THIRDPARTYLICENSE.gladman) for x86 table/
key material; [OpenSSL standalone notice](THIRDPARTYLICENSE.openssl) and [full assembly notice](NOTICE.aesni)
for AES-NI; BSD-2-Clause original wrappers/recipes. These terms are retained, not
relicensed. This product includes software developed by the OpenSSL Project for
use in the OpenSSL Toolkit (http://www.openssl.org/).

Next real scoped entropy/provider work and the remaining engine feature/admission
closure. Engine startup remains unavailable until those are implemented; current
large backing/child/lifetime limits still cannot fit the measured host profile.
No new external SDK or companion blocker is established by these component results.
