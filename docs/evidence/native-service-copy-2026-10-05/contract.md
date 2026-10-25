# Checked page-fragment native input copies

Before-code scope,2026-10-05. R1-03 dynamic thread schedules have retained30-second
deadline failures. Native mask8-byte and storage64/96-byte descriptor reads repeat
owner mapping lookup for every byte; larger-owner metadata makes this needless
repeated work. Coalesce these two inputs at4 KiB boundaries, with unchanged native
rights, pointer/error/effect order, quotas, native formats and public ABI/SDK/pins.
This is a scoped implementation change, not a general VM/user-copy framework or
proof that copying is the only runtime bottleneck. No sibling changes.

Add one private input-copy helper receiving the actual State owner and a kernel-
local destination. Reject pointer overflow, find the readable backing page for
each fragment, and copy only to that page boundary. A second page must be validated
separately; never assume adjacent virtual pages share physical backing or rights.
Partial failure affects only a caller's temporary kernel stack array; no descriptor
admission/mask/output effect is exposed until the complete input is snapshotted.
Inputs cannot alias those kernel stack arrays, and no pointer survives this IF-clear
owner-serialized operation. No persistent index, new authority table or allocation.

Signal output has exactly8 bytes, spanning at most two pages. Validate writable
first/last bytes before the existing chunked write and before changing mask; retain
input/output overlap semantics. Keep original unsupported-how, reserved fields,
foreign/stale grant, overflow and denial ordering. Descriptor64/96 grammar and
original pointer preflight remain. Actual clone validates all storage and rights
before publishing a native ID or writing caller TID. Do not alter clear-TID,
retirement, scheduler, aliases, physical backing or byte lookup itself.

Tests: actual cross-page mask input/output alias, readonly/no-access second page,
wrap and unchanged state/output; valid cross-page96-byte actual musl clone card;
invalid second-page clone EFAULT with actual upstream EAGAIN, unchanged output,
admissions and mapping budget; a private error-suppression control must fail371.
Fresh repeated two-round service schedule, prior seven dynamic controls, maintained
memory/pair/lifecycle groups and stack/storage/signal-mask profiles; wrong-mask
inheritance remains an actual kernel mutant. Source/tool/SDK freeze,180/30/3-second
build/guest/teardown budgets, retain all failures, full host/pins/workflow/format/
simplicity/links, then every-member archive readback before owned duplicate cleanup.
Missing reader/consumer and stress coverage remain explicit, not blanket adoption.

Simplicity: retain byte-by-byte code if coalescing cannot preserve its behavior.
For these fixed inputs it adds repeated lookup without a safety benefit; one short
page-fragment helper and endpoint validation for an8-byte output remove that work.
Borrow the existing boot copy's page-boundary chunking but return checked failure
for untrusted input instead of panicking. No general address-space abstraction,
new ABI, bulk syscall or service is needed. Existing immutable evidence stays;
remove only the two superseded local per-byte input loops and redundant8-byte
output validation loop. Actual host/guest intervals are fixture observations,
not calibrated syscall latency, stack high-water or WCET.

Before attempt2: nine fresh cases pass, including cross-page masks/descriptors
and actual EFAULT/EAGAIN descriptor denial. The error-suppression control instead
fails at strict ELF admission. Optimization removes the initialized cookie because
later thread paths are unreachable; LLD emits a tbss-only TLS view outside a LOAD.
Retain invalid ELF/ISO/raw logs; this is not semantic371 coverage. Check actual
initial cookie17 at main entry, preserving initialized TLS in every fixture.
Keep loader validation and kernel copy code unchanged; all twelve cases rerun.

Before attempt3: ten cases pass on attempt2, but missing-native-mask control times
out after successful worker results. The actual omission flag is present. Musl
start restores the creator's saved application mask, hiding initial native
inheritance loss from the later callback check. Snapshot actual blocked creator
mask through its held grant before clone, publish with record metadata, and check
the child's mask in native trampoline before calling musl start. This adds no
kernel authority or ABI. Record failed controls as failures, not evidence that the
omission is safe. Native Debug source copy code remains unchanged; rerun all12.

Before attempt4: all eleven copy/dynamic/boundary/rejection cases pass in attempt3;
repeated dynamic service still exceeds30 seconds after its first successful service
terminal and replacement admission. Coalescing does not close this stress gate or
establish its sole bottleneck. Record the stress case as blocked-deadline and the
complete target packet as partial, never pass. Preserve its failed attempt; finish
copy correctness and required regressions with that gate explicitly open. Also
exercise cross-page masks and real clone cards with caller DF=1: existing vector
entry clears DF before kernel copies, and the private trap clears restored user DF
before returning to C. No assembly/kernel entry change; libc and compiler copies
never execute under an invalid C direction-flag state. All11 semantic cases rerun.

Before attempt5: nine cases pass in attempt4, including DF-set cross-page clone.
The suppressed-span fixture then fails compilation on an unused DF helper: the
intended mask alias substitution did not match formatted source. Make the first
alias mask operation actually call the DF trap, including the negative fixture,
and rerun all12. Preserve the failed compile; kernel implementation stays frozen.
