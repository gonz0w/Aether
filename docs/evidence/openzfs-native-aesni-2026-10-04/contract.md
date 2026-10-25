# Native AES-NI component contract — before implementation, 2026-10-04

R1-03 selected CPU-state qualification. Compile unchanged OpenZFS 2.4.4 AES-NI C
callbacks and their actual x86 assembly from sealed sources. Reuse independent
128/192/256-bit known-answer vectors from the sealed generic AES packet. Invoke
only supported real callbacks. qemu64 must reject 238 before any AES-NI callback;
QEMU max must advertise AES, upstream is_supported must accept it, and OSXSAVE/AVX
must remain disabled. Actual hardware AES uses the existing XMM context contract.
No XSAVE, ABI, quota, kernel, SDK pin, sibling or default image change.

Check key expansion rounds, independent encrypt/decrypt results, in-place buffers,
input/schedule immutability and canaries in both isolated native contexts. The
internal generic/accelerated word order differs; use exact public-vector bytes
and explicit conversion according to the upstream needs_byteswap field. Fixed
valid key sizes only; never pass unsupported sizes to low-level callbacks. At
least 64 complete repetitions and four advancing virtual ticks, bounded by 100000
repetitions. Preserve existing TLS/memory/64-yield/output/terminal oracles. Max
corrupted ciphertext/plaintext must reject 241/242; frozen clock must reject 244.
All negatives require exact ordered terminal/panic checks, not generic failure.

Audit actual AES-NI C/assembly objects: require real AES instructions and reject
AVX/AVX512, XSAVE/XRSTOR/XGETBV or unsupported extended register state. Timer
progress shows workload spans interrupts, not every instruction. This qualifies
component operations, not initialized-engine dispatch, AES-GCM/authentication,
all algorithms/tunables, constant-time behavior, side-channel protection or FIPS
certification. AES-NI availability alone is not full crypto-service admission.

Security/ownership: no new authority or ambient provider. Callback pointers name
local linked code, not capabilities; buffers are aligned owned fixed-size objects.
Original assembly and ABI remain unchanged. No allocations, engine startup, volume,
private secrets or new concurrency/lifetime mechanism. All test keys are public.
Simplicity SE-01–05: first test a proven existing XMM implementation instead of
adding extended kernel context machinery or a crypto service. Direct genuine ops
and existing fixture suffice; no dispatch framework or successful unsupported stub.
No old compatibility path is removed; cost is private port qualification evidence.

Verify prior complete seals/archives before regular-file selection. Freeze all
inputs through qualified builds/target runs; preserve every failed attempt. Retain
OpenSSL-standalone assembly and CDDL C notices separately from original BSD wrappers.
Full host/pin/workflow, scoped formatting/syntax/source identity/simplicity/links
before sealing. Read every new archive member and verify reused bytes against
original members before deleting only this owned duplicate root. Update existing
STATE/ROADMAP/FEASIBILITY/third-party record; no new maintained launch/script entry.

## Actual dispatcher, before implementation

Extend this same private CPU-profile experiment to unchanged aes_impl.c and its
real generic/x86 callbacks and assembly. Run aes_impl_init before public key/block
functions, verify default fastest and explicit generic/AES-NI choices against the
same independent vectors, and reject unknown/unsupported names honestly. Baseline
must select the real x86 implementation; max must select AES-NI. Assertions use
only the already qualified private fatal diagnostic, never successful stubs. No
engine/spa initialization, queue/thread/heap expansion or mutable global kernel
state. User-space dispatcher state is private to each existing native domain.
Named selection is user-space algorithm policy, not capability authority.

Retain prior callbacks-only attempt unchanged. Fresh source/recipe snapshots and
independent native cases: default dispatch qemu64/max, explicit generic qemu64/max,
explicit AES-NI max, malformed/unsupported selection checks, corrupted encryption/
decryption and frozen-time controls. Frozen target inputs and exact terminal
oracles remain. Audit the actual x86/AES-NI/generic code and classify any added
imports before execution. The whole-engine CPU profile is still not closed.

Dispatcher attempt1 exposes upstream aes_impl.c's int/size_t comparison under
-Wextra -Werror. Its bounded loop visits three immutable array entries; no counter
or authority input is untrusted. Preserve that failure. Compile only that upstream
translation unit without -Wextra, retaining -Wall/-Werror and all existing target/
safety flags. The already qualified private CDDL assertion translation unit keeps
its prior warning profile (unused assert_lock is in its historical fatal-only port).
All new original C and other imported crypto units retain -Wall/-Wextra/-Werror.
This is scoped upstream-profile compatibility, not blanket suppression or a source
rewrite. Recorded commands/source identity and runtime tests remain mandatory.

## Public buffer boundaries, before implementation

After the passing dispatcher run, add misaligned public block encrypt/decrypt with
canaries and exact key/plaintext/ciphertext sizes placed immediately before a real
PROT_NONE guard page. Reserve three grant-backed pages, enable only the middle
page, then unmap all three and require exact caller availability restoration.
All normal/error paths own that mapping explicitly; deliberate one-byte-past-key
read must produce native #PF, both terminal kind2/detail142 before the profile
panic. This control verifies actual guard enforcement rather than a canary-only
model. Existing kernel termination/zeroing handles deliberately faulted contexts.
No untrusted pointers, new authority, quota or public behavior is introduced.
The fresh full dispatcher matrix adds this guard control; retain earlier passing
matrix and source snapshots. These boundaries are a current crypto FFI requirement,
not a new memory framework or general fuzz/sanitizer claim.
