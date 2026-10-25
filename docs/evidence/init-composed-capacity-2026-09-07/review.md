# SI-06 implementation and stack review

The scoped runtime.patch compares this change with the retained two-pool source
snapshot, excluding unrelated earlier working-tree work. This is the implementing
contributor's review, not independent sys-init or maintainer sign-off.

The parser accepts the new magic only with its exact two-ELF 56-byte envelope.
All component lengths are checked before slicing. On the x86_64 target, the two
1 MiB ELF bounds and 16 KiB code bound keep the subsequent usize sum well below
overflow; an unbounded u32 code length rejects before addition. V1 and V2 retain
4/8 KiB limits; tests exercise each identifier separately. No general native-C
ELF allowance or worker authority is used to bypass the init contract.

The supervisor mapping loop already maps exactly ceil(code_bytes/4096) pages.
V3 uses at most four RX code pages and one RW/NX stack in the existing 128-page
arena. There is no additional arena allocation or quota increase. All kernel code
aliases become RO/NX before entry. Every code-page flag/address and alias is
verified; partial-page tails are verified zero. The existing dirty-tail control
also applies to V3. The fixture executes jumps on pages one, two and three before
running the Rust lifecycle code from page four. Actual writes to each added page
fault with error 7; stack execution faults with hexadecimal error 15 and a write
below the stack guard faults with error 6, followed by verified shutdown.

The init owner/worker indices and grants remain unchanged. Existing closeInit
first closes admission and detaches roots, restores kernel aliases, then zeroes
and verifies every backing page, so its loop covers all four code pages without
a special count or alternate cleanup path. Normal completion retains the mapped
supervisor and halts; it is not whole-domain reclamation. V3's only new runtime
identity/state is its profile flag and ABI/marker selection. Old markers retain
exact bytes. No new unsafe Rust, FFI, assembly runtime path or public operation
is introduced; small instruction-byte fixtures are conformance inputs.

## Separate composed-stack witness

consumer-study.tar.gz retains a private copy of sys-init decision 0174's refined
candidate, its original sources and exact build commands. Only the expected ABI
value changes from 15 to 16 and the linker code assertion from 8192 to 16384.
The positive remains 11,680 bytes. Helpers come from the retained 0173 envelope;
input.json binds that envelope and each helper hash. No sibling source or pin is
modified and no sys-init candidate is promoted into its maintained path.

On the current producer, all six copied candidate cases run without a native
fault: positive Terminal/reclaim-capture composition returns 100/reclaimed=3;
wrong-owner, unsealed-source, dropped capture, corrupted capture and interrupted
sample controls return the exact 1094–1098 results with reclaimed=0. The candidate's
own checks validate repeated delivery and retained application/source association.
Raw serial and artifact hashes are retained per case. An earlier positive probe
is also retained, separate from the six-case qualification.

These are actual executions using the unchanged one-page stack and selected
nested calls. The supplemental candidate-assembly.s/stack-inspection.json confirms
that _start reserves 64 bytes and saves one register; the called composition
saves six registers and reserves 3,288 bytes. Including the call return address
and initial stack offset leaves RSP at stack-base + 672 before deeper calls.
That offset is not unused headroom: nested calls consume more. No stack high-water
measurement, arbitrary recursion, future reclaim/Cleaned composition, every possible
interrupt schedule or production headroom claim is made. Do not enlarge the stack
or infer that later additions fit from this bounded pass. Sys-init independently
owns review, source rebuilding, its full affected regressions and acceptance.

## Offline handoff boundary

The producer source archive contains regular source, tests, current references,
reviewed standards snapshots, planning and pinned boot dependencies. Historical
evidence directories are excluded and separately retained in this packet; they
are not executable build prerequisites. Its planning text records the frozen
pre-qualification point; this packet's README/producer.json records the outcome.
Source and SDK archives are safely extracted to fresh private roots and the full
new-profile suite is rebuilt there. This is a same-owner offline reproduction,
not an independent consumer build or a bit-identical ISO claim.

The old SDK's absolute obj/Makefile link is retained in the failed-extraction
archive. The new archive changes only its target spelling to the equivalent
relative ../musl-1.2.6/Makefile. Regular SDK bytes stay identical and hash-verified.
Installed tool identities/paths remain pinned; tool hashes do not establish the
entire host/toolchain library closure. Original BSD-2-Clause work, musl and boot
third-party notices keep their own terms. No release publication is implied.
