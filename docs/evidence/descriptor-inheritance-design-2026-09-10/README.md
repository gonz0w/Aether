# Command descriptor inheritance review — 2026-09-10

This documentation checkpoint selects the next bounded native experiment in
[NATIVE-SHELL-STARTUP](../../NATIVE-SHELL-STARTUP.md#command-descriptor-inheritance-selection--2026-09-10).
No runtime implementation, wire ABI, SDK adoption or new native acceptance is
claimed. The prior local rebinding packet remains the latest target evidence.

Source inspection found four concrete integration requirements:

- Keep descriptor slots, duplicate counts and FD_CLOEXEC flags private, while one
  user-space owner holds the shared stream positions and backend lifetime.
- Stage child holders before kernel copy, then activate its private alias route
  before processing requests. Neither wrapper exposes application-level completion
  until the child has rebound and the owner acknowledges readiness.
- Release only staged resources on pre-copy failure. After publication, confirm
  child stop before dropping its holders or reusing memory/channels.
- An uncertain backend result affects every alias of that shared description;
  closing one client's last local alias must not invalidate another holder.

The selected source/backend/copied-child witness fits the existing three workers
and six channels. Exact request/receipt layout and code are the next work. The
acceptance sequence tests shared abcdef positions, FD>=10/CLOEXEC preservation,
independent closes, one final backend close, rejection/rollback, publication failure
and repeated reuse. Current raw-copy fixtures remain independently consumed.

The simpler alternatives fail existing requirements: copied positions or reopened
backend streams lose open-description identity, a kernel descriptor table moves
policy into the kernel, and an extra kernel pause mechanism is unnecessary with
explicit wrapper completion gates. The additional bounded user-space alias and
transaction state is justified by this next experiment. Production service ownership
and SDK adoption still require the affected owners; no sibling files were changed.

Verification: `zig build test --cache-dir .zig-cache --global-cache-dir
.zig-cache/global` passes 98 Python tests plus Zig/pin/workflow checks;
`git diff --check` passes. checks.json retains exact commands, UTC/elapsed/status
receipts. The four-file simplicity snapshot and previous evidence manifest are
verified separately. No QEMU run is selected for documentation-only changes.
Runtime/build source inventory is compared against the prior sealed rebinding
packet rather than presenting its target passes as new runs.

sources.tar.gz retains the inspected local files and relevant userland documents
with hashes and archive readback. Existing standards bytes and release pins remain
unchanged. The final manifest binds this review packet. Missing owner/reader review,
full fork/exec/wait, inherited descriptors, shared-close runtime coverage and R1
release gates remain open.
