# Host static-C launch profile

UL-020: executable host model supporting UL-003. This validates and prepares
the **format** of a proposed launch, not the native transport adapter. It neither
maps guest pages nor starts tasks, sets FS, grants authority or consumes sys-init
descriptors. Linux-reference machine code still contains Linux syscall entries
and cannot be booted as native Aether merely because this check passes.

Run from the repository root, with the pinned reference ELFs available:

```sh
python3 experiments/launch-profile/check.py
```

The script checks source artifact hashes before inspection and saves plans,
initial-stack bytes and evidence in a new build/launch-profile-* directory.
It materializes segment zero/copy operations in ordinary host byte arrays only.
No target or sibling files are changed. Retained [evidence](evidence.json) and
[startup plan](startup-plan.json) are available for companion review.

## Proposed host-static-c-v0 limits

These are local experiment constants, not allocated kernel ABI values. Narrow
limits make the first consumer reviewable; they are not final limits for Zsh.

| Item | Proposal |
| --- | --- |
| Input | ELF64 little-endian, System V ABI tag, x86-64 ET_EXEC, at most 1 MiB |
| Program headers | Exact ELF64 sizes; 1–16 entries entirely in file |
| Image address range | 0x00200000 through 0x40000000 exclusive |
| Page size / budget | 4096 bytes; at most 16 MiB of image plus stack mappings |
| LOAD | R, RX or RW; page-congruent file/virtual offsets; no page overlap |
| Alignment | Zero/one or power of two at most 4096; stricter than general ELF |
| Initialization | Zero entire fresh mappings, then copy each declared file range |
| Entry | Must be within file-backed bytes of an RX LOAD |
| Program header view | Exactly one PT_PHDR, readable inside a LOAD with identical file bytes |
| TLS | Exactly one readable template, nonempty and at most one page; initialized bytes and memory extent inside LOAD |
| Stack | Explicit non-executable GNU_STACK; 64 KiB at 0x70000000, proposed unmapped guard immediately below |
| RELRO | At most one range; covers all live bytes of any affected RW LOAD pages; final permissions R |
| Optional metadata | Bounded, file-backed GNU_EH_FRAME accepted; not an unwinder implementation |
| Other segments | Rejected, including dynamic loader/interpreter and unknown extensions |

The profile intentionally requires TLS even if another C program would not;
the first consumer tests musl's thread-pointer setup. Source alignment and bounds
checks use overflow-safe comparisons; large fields cannot drive arbitrary host
allocation. Section tables are not consumed: this is a program-header model,
not a general ELF object/linker validator or machine-code verifier.

A real loader must initialize through privileged loader-owned mappings and remove
writable aliases before execution; host byte-array initialization does not prove
that property. RELRO is applied before entry for this already-relocated static
profile. A future dynamic or static-PIE profile needs its own relocation contract.

## Initial stack

The model produces an aligned RSP pointing to argc, followed by argv pointers,
a null pointer, env pointers, another null, and terminated auxiliary-vector pairs.
Strings and 16 entropy bytes are copied into the same stack allocation.
Arguments/environment are bounded to 16 each and 8192 combined string bytes;
embedded NULs, duplicate environment keys and malformed environment entries fail.

Auxv supplies mapped program-header address/size/count, page size, entry,
real/effective UID/GID, secure-state, random-byte address and executable-name
address. The host test uses UID/GID 1000, AT_SECURE=0, and public bytes 0–15 as
deterministic entropy. **These are fixtures, never production credentials or
entropy.** A real launcher obtains identity and randomness from authorized
services; neither UID 0 nor these metadata fields confer native capabilities.

The template stays in the loaded image. Musl copies it into its initial TLS
storage during startup; the model does not allocate a native thread pointer or
pretend that descriptor/clear-TID semantics are provided by stack generation.

## Test evidence

Both real startup and allocator ELFs pass. Tests decode the generated stack,
verify args/env/auxv and pointed-to strings/entropy, compare loaded program-header
bytes, check the TLS initializer (17), confirm zero padding and deterministic
test output, and confirm final TLS-template page protection.

Forty-six negative inputs cover truncated/oversized headers, machine/class/endian,
table bounds, unknown/dynamic segments, file/memory ranges, alignment, overflow,
page overlap, mapped quota, wrong permissions/entry, missing/duplicate/unmapped
special segments, unsafe RELRO and malformed/oversized startup inputs.
This finite suite is not fuzzing coverage or production-loader security proof.

Consumers should review [native handoff](../../docs/NATIVE-C-HANDOFF.md) alongside
these artifacts. The exact host profile can change during that review; no sibling
implementation or lifecycle v1 modification is assumed.
