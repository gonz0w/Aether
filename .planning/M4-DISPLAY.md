# M4 first slice: a separate Rust display service

The [live display slice](M4-LIVE-DISPLAY.md) now extends this baseline with a
concurrent fresh publisher, two endpoint grants and checked results/acknowledgments.
Lifecycle v1 remains unchanged. The paragraphs below define the original display
setup; the live slice supersedes its stopped-AP and completion-marker limits.

After M3 acceptance, stop the BSP fixture and disable its endpoint table. Launch
one fresh, statically reserved BSP display domain from a second immutable Rust
boot module; do not reuse M3 code, stacks, or page tables. The AP remains stopped.
This slice demonstrates framebuffer delegation/rendering, not live worker status
messages or supervised restart; those remain required for the full M4 POC.

Bootstrap validates 32-bit RGB geometry and the framebuffer memory-map entry,
copies the display image before dropping boot mappings, and records a bounded
framebuffer grant. Require a page-aligned physical start and at most 2 MiB after
page rounding. Reject overlap with any non-framebuffer memory-map entry. The last
page may contain framebuffer padding; authority is page-granular, not byte-exact.
This bound covers the pinned 800x600 emulator; larger modes fail explicitly.

The display domain has two typed framebuffer references: map+inspect and
inspect-only. int 0x80 RAX=40 maps the recorded span at 0x02000000 with user RW,
NX, UC permissions; RAX=41 inspects its byte count. RDI holds the reference;
RAX returns 0 success, 1 invalid, 2 denied, or 6 already mapped; RDX returns
address/byte count or zero. No caller supplies a physical address, length, or
permission bits. Other domains have no such grants. No unmap, transfer, or reuse
is supported in this slice. Boot entry registers carry validated geometry and
mask shifts as immutable values; they convey no additional device authority.

The service checks invalid/foreign handles, inspect-only mapping denial, and
duplicate mapping rejection, then draws the color pattern and an AETHER / RUST
DISPLAY heading using volatile stores. Default SMP boot performs no kernel
framebuffer drawing. The one-core historical baseline retains its M1 pattern.
The service deliberately writes to the first unmapped page beyond its grant;
the kernel requires a user non-present write fault before accepting completion.
The AP M3 fixture also probes the unmapped display address before its transport
and APIC checks. Normal clients cannot invoke a kernel drawing operation.

Smoke requires AETHER DISPLAY PASS and validates actual pixels, including a new
user-only accent. Withholding map rights must fail in the guest. Skipping Rust
drawing must fail screenshot validation even if the service reports success.
A separate service ABI/loader and client display-message protocol are deferred
until their next concrete use. This is firmware-framebuffer output, not native
NVIDIA display support.
