# Bounded Zsh application profile

This experimental resource composition is selected by
`-Dnative-fs-application-profile=true` with the complete existing ABI31 filesystem
owner-stack flags and a matching `AENFS006` envelope containing `AENMX011`.
The [approved engineering decision](../PROJECT.md#bounded-zsh-application-trial-2026-10-25)
and [exact profile](native-zsh-application-v1.json) define its bounds.
[Issue69](https://github.com/gonz0w/Aether/issues/69) owns implementation and
verification; [issue65](https://github.com/gonz0w/Aether/issues/65) owns the Zsh
link handoff. The profile provides capacity; it does not implement missing shell
or filesystem semantics.

## Resources and selection

| Resource | Selected application profile |
| --- | --- |
| Application ELF file | At most 1.5 MiB |
| Image plus existing main stack | At most 384 backing pages |
| Total backing per application | 640 pages; five equal application slots |
| Image virtual window | `0x200000..0x400000`, upper bound exclusive |
| Anonymous virtual arena | `0x10000000..0x10280000`, upper bound exclusive |
| Existing main stack | 16 mapped pages; initial downward space is 48 KiB |
| TLS template / leaf tables | Existing 4 KiB / 32 limits |
| Engine / owner backing | Existing 8192 / 128 pages |
| Aggregate assigned backing | 11520 pages / 45 MiB |
| Existing reservation / ungranted tail | 64 MiB / 19 MiB |

The maximum image leaves at least 256 backing pages for all later runtime
allocations, including TLS, allocator metadata and guards. This trial allowance
is not a measured heap requirement. The anonymous arena's virtual size is not
additional backing. Query reports actual remaining capacity after image, stack
and anonymous occupancy. The mapped stack does not give 64 KiB of free downward
call-stack space; bootstrap data, signal frames and recursion remain relevant.

Old ordinary and filesystem profiles keep their defaults, selectors, wire formats,
limits and seals. The input cannot opt itself into a larger budget. Kernel build
selection, outer and nested formats must match before effects. The owner ABI31,
AFSRPC09 and AEFW0001 wires are unchanged. No production release or guest is
selected by this build flag.

## Ownership and failure behavior

Each application retains one authoritative kernel state, its private backing and
caller/generation-bound memory grant. Equal process pools support the existing
private page-copy operation. Launch, exec and copy validate selected image, role,
capacity, layout and ownership before reset or publication. Mutable image, heap
and TLS pages remain private; immutable user mappings and kernel aliases preserve
their protections. Child rebind retains checked auxv, TID, TLS, descriptor and
channel ordering. A failed staged copy remains unpublished and is zeroed.

The filesystem engine and process owner retain their existing roles and grants.
A larger application quota confers no engine, factory, block, console or filesystem
authority. Allocator slice bounds prevent applications from using engine, owner
or retained-tail pages. Exhaustion and stale/foreign grants fail without partial
effects. Terminal observation, mapping cleanup and confirmed reclaim remain
distinct; reclaim invalidates grants and zeroes the entire owned partition.

Only this selection enlarges three application staging buffers to 1.5 MiB each.
Final kernel/boot footprint inspection must include that additional 1.5 MiB,
metadata and actual module/envelope bytes under the existing kernel mapping
bound. No shared-code/COW mechanism, general allocator or global process table
is introduced.

## Verification and use

Run the affected actual-path host controls from the repository root:

```sh
python3 -B -m unittest discover -s tests -p test_fs_application_profile.py -v
```

The `kernel-check` build step depends on the actual configured kernel compiler
step and performs no installation or guest execution. For this profile, use the
existing flags from `scripts/fs_home_inputs.py:kernel_flags()` plus the explicit
application flag and matching selected envelope. Retain an owned cache/output
root and inspect the emitted kernel ELF before cleanup.

Use the pinned toolchain and separately provisioned private dependency inputs.
The owning issue selects old/new ELF/envelope boundaries, wrong-profile and
role/grant denials, allocator exhaustion, copy rollback/rebind/reclaim and actual
kernel compile/footprint checks. The complete host gate is `zig build test` on
frozen inputs when its exact private normative prerequisites are available.
[Public input availability](PUBLIC-SOURCE.md) and the explicit
[current host input association](FILESYSTEM-HOST-INPUTS.md) apply. Public CI checks alone do
not replace the complete affected host or native stages.

Build actual Zsh with the [authenticated closure](../userland/docs/ZSH-CONSUMER.md),
then inspect the newly produced ELF and envelopes using the selected parser.
Keep exact SDK, compiler/provider associations and artifact measurements in local
compact evidence. No target configure execution, fake syscall success, provider
substitution or mandatory-feature removal is allowed. Remove owned generated
outputs; disposed artifacts are historical evidence, not runnable deliverables.

Native heap/stack peaks, copy latency, IRQ behavior, TTY/ZLE, libc stdio/exit,
filesystem operations and an assembled persistent boot-to-Zsh ISO remain separate
acceptance gates. [Issue64](https://github.com/gonz0w/Aether/issues/64) owns the
matched native filesystem prerequisite; this host-only profile grants no guest.

## Scoped host result —2026-10-25

A fresh build of the required authenticated Zsh closure passes the explicit
application parser; the ordinary default still rejects it. Actual-image file,
page, window, permissions, TLS and framing controls pass, including validation
of all three application image slots. The configured application kernel compiles;
staging and metadata sizes and the existing kernel mapping bound are inspected.
Exact SDK/artifact measurements and receipts remain local.

These are focused host results. The structural envelope uses a small engine and
owner placeholder; it is not a matched runnable engine/owner composition.
The complete root host gate reached its existing 300-second aggregate deadline
and remains failed/incomplete. Focused diagnosis found a missing selector
classification and unavailable local regression prerequisites. Their corrections
and a refreshed input association do not replace a complete passing gate.
Final integration review remains pending under issue69/issue70; native acceptance
remains separate.
