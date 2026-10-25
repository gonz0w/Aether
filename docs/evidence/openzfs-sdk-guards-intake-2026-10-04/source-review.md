# Corrected guards and remaining startup boundaries

Selected candidate seal:
f6bc6d6da3b051e1e4617e60ae256cbd35d193b608631ac29f7c42dbe73b13dc.
The staged libc SHA256 is
2459a32ba53cfc1dd62160d4bb8ea8e1afbac3615f2784c7351ad04f91183719.
Old libc8f66b2b383eabd08b8f27c4913f36a91071c4cfb6373cedebd2e69cabfaaeecc
remains unchanged. This is independent scoped candidate consumption, not default
SDK promotion or a release-pin change.

Actual source inspection finds the realtime fallback now retains the
gettimeofday return and propagates a negative result before conversion. Both
physical/available-page sysconf branches test __lsysinfo before accessing its
result. The native paired positive image observes actual ENOSYS and unchanged
buffers; the same realtime check with old libc exits240, and the old page check
exits241. Every failed query stays unavailable. Other sysconf branches and general
overflow/concurrency/provider semantics are outside this acceptance.

The independent archive reader preserves each ordered occurrence. Both libc
archives contain1349 objects with1346 distinct names (free/realloc/clone duplicate
basenames). Only clock_gettime.lo/sysconf.lo change; all other staged bytes and
object occurrences match. Flattening ar extraction would lose those duplicates.
This comparison is byte evidence, not certification of all unchanged SDK code.
Verified recipe/patch/source metadata is retained as inert input; no sibling build
recipe is executed and no sibling is edited.

## CPU-state review

The actual relinked executable still contains AVX/YMM/ZMM and xgetbv instructions.
The instruction inventory records682821 decoded sites and35086 candidate extended
sites; these counts describe disassembly only, not execution or unsafe selection.
Changing libc error guards does not remove the engine's accelerated implementations.

The native runtime requires CR4 OSXSAVE clear before admission and uses
fxsave64/fxrstor64. Its established contract supports x87/SSE, not extended state.
The verified upstream libspl sys/simd.h has __simd_state_enabled check CPUID
OSXSAVE before xgetbv; AVX/AVX2 and AVX512 helpers gate on the required enabled
state. Reviewed GCM selectors also call those availability helpers. These source
guards are promising compatibility evidence, not native crypto dispatch testing.
kfpu_allowed() is always1 in this user-space header and is not a substitute for
the extended-state checks or a native feature-profile review.

The archive retains those original source bytes, configuration and actual linked
instruction inventory. AES/GCM source inspection covers only the named paths;
other checksum/compression/hash selectors, manual tunable choices, initialization
benchmarks and preemption schedules remain unqualified. The simplest next native
profile should retain portable algorithms or prove each selected x87/SSE path;
adding XSAVE/AVX kernel context support merely to make a startup audit run is not
justified by the present requirement. No CPU-state feature is added or waived here.

## What blocks engine execution now

The two reproduced SDK error paths are corrected and independently qualified in
the specified scope. Their providers are still missing. Native public monotonic
clock remains EINVAL; raw clock/gettimeofday/sysinfo, uname/getentropy and random
device open still return ENOSYS. No actual time, capacity, identity or entropy
is supplied by this delivery. The engine must not execute with fake values or
zero-initialized substitutes for required providers.

Aether's next work is the native feature/CPU-state profile and explicit owner-local
resource/time/entropy/configuration contracts, then their enforcing primitives and
user-space bindings. Real measured memory/stack/thread admission and startup/fini/
restart remain required before granted pool/config I/O and Rust filesystem service
composition. The739 pages left after loading the image do not establish capacity
for the selected host-measured engine. Userland's other sysconf branches and
production runtime bindings need their owner's review when that contract is defined.

Independent SDK guard intake is no longer an external blocker. The current engine
experiment stops at missing/unsafe-to-assume prerequisites; local profile/provider
work remains possible. No assertion of a mounted filesystem, useful persistent
shell/package path, unrelated-project blockage or complete R1 readiness follows.
