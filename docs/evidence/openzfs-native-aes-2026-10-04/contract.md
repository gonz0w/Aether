# Native generic AES component, before implementation — 2026-10-04

R1-03 CPU-profile work. Execute unchanged upstream OpenZFS generic AES key schedule,
encrypt and decrypt callbacks with independent FIPS197 AppendixC known-answer
vectors for128/192/256 bits. Select the genuine generic operations object directly;
do not replace the algorithm, fake engine dispatch initialization or invoke engine
startup. Validate both encryption and independent ciphertext decryption, in-place
operation, input/key immutability and surrounding canaries. Valid fixed key sizes
only; no unsupported size is passed to a low-level callback.

Run both native isolated contexts on qemu64/max with the guarded sealed SDK and
verified original headers/source. Retain TLS/memory/64-yield/output/terminal checks.
Require correct repeated computations across at least four advancing virtual timer
ticks with a bounded100000-iteration ceiling. This witnesses interrupted workload,
not interruption of every instruction or complete SIMD preservation. Corrupt only
encryption/decryption outputs as controls241/242; frozen virtual-clock control244.
Exact ordered terminal/panic oracles are required. No private key material/logs;
all test keys are public vectors. Do not use these vectors as runtime entropy.

Security: no new authority, syscall, memory/thread quota, SDK or kernel change.
All buffers are aligned local fixed-size arrays; callbacks receive only their
valid object/round bounds. No allocation/callback/lifetime/thread ownership changes.
Generic AES has secret-indexed tables: successful vectors are not constant-time,
side-channel/security certification or approval for production encrypted pools.
AES-NI/other accelerated modes, GCM/authentication, other crypto/checksums, tunables
and actual engine selection/admission remain separate qualification work.

Simplicity: test the actual smallest algorithm component rather than adding a
crypto service or extended-state machinery. No framework/registry, fallback stub or
normal-image dependency; direct existing callbacks and native fixture suffice.
Added cost is private profile evidence only. Preserve CDDL/public-domain upstream
notices and BSD-2-Clause for original recipes/probe. Verify complete prior seals and
archives before selective regular copying; preserve every attempt and freeze all
inputs through qualified target runs. Full host/pins/workflow, scoped formatting,
syntax/source identity/simplicity/links before sealing. Read back all new/reused
members before deleting only this owned duplicate workspace. Update existing STATE,
ROADMAP and FEASIBILITY, not a parallel status tree.
