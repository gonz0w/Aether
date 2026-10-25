# System repository consolidation

Maintainer authorization: consolidate Aether, Aether-userland, sys-init and
pkg-mgr in Aether; keep Aether-standards separate, preserve history and pins,
and remove generated outputs. Other agents are paused for the migration.

## Requirement and review before implementation

Keep the kernel at the repository root and import the other components under
`userland/`, `sys-init/` and `pkg-mgr/`. One integration change may now span these
directories. Component responsibilities, capability boundaries, language choices,
release requirements and native experiment limits remain unchanged.

Preserve original commit IDs and all source refs in namespaced Git refs. Capture
uncommitted work before adapting it. Do not rewrite history, push, change standards
release bytes or pins, modify Aether-standards, grant new runtime authority, or
claim boot/release qualification from repository checks. Preserve sealed inputs
byte for byte; historical absolute paths require explicit relocation when consumed.
Do not rewrite immutable evidence to make it look newly qualified.

Generated caches, temporary builds, old images and unpacked test output are
disposable. Keep maintained dependency and current delivery directories distinct
from disposable test evidence. Preserve compact results and failure records.
Original working trees remain recovery sources until imported bytes and refs have
been verified. Never delete unknown personal files or live package prefixes.

The simpler alternative is a parent workspace with four independent repositories.
It leaves the repeated source/ABI handoff and revision coordination that motivated
this request. Keeping the existing kernel paths and importing component folders
avoids a wider kernel/build rewrite. This removes repository ownership barriers
without combining runtime services or introducing new mechanisms in the kernel.

## Validation selection

Verify imported refs and working-source hashes; compare all offline standards,
review snapshots and current dependency seals before and after relocation. Run
affected path/checker tests and each component's offline quality checks, followed
by one broad host integration checkpoint. Native payloads are not changed or
qualified by this migration. Record any unresolved path or evidence-replay gaps
explicitly. No QEMU retry or persistence campaign is authorized by this review.

Documentation impact: root README, AGENTS, DEVELOPMENT, companion ownership and
STATE explain the single source tree and integration workflow; component guidance
retains local contracts without requiring cross-repository handoffs. Existing
component backlog IDs stay stable.


## Result and limitations

Source import and original refs are verified in the linked JSON receipt. All564
frozen release/review inputs match their pre-migration blobs. The integration
merge preserves original commits and working snapshots without rewriting history.
Current component guidance, paths, Make targets and the provenance relocation
library are implemented. Its seven exact historical tooling inputs total93229
bytes; no kernel/service/ABI/binary substitution is allowed. This compatibility
path preserves sealed artifact provenance, while fresh qualification still checks
live code. Two obsolete ABI30 test scaffolds were repaired without kernel changes.

Userland quality, nine sys-init current-source gates,79 historical-parser regression
methods and61 affected kernel methods pass. The initial broad run's162 Zig tests
pass, but its916-method host run fails; the affected corrections are tested once
as a61-method batch. Two old AF07 live-source intake methods remain blocked by
pre-existing ABI30 kernel drift, verified against the pre-migration snapshot. Their
pins remain fixed. A fresh matched owner/build is needed; no gate was weakened to
accept changed kernel code. No new native or release claim.

The package full suite times out at its existing600-second watchdog after substantial
passing checks. Its source-preview export also exposes an existing incomplete
allowlist. These are recorded coverage gaps; no budget increase or automatic full
retry. No source-preview publication or broad package-policy change was made.

Generated cleanup removes106685537548 logical bytes of old per-run builds and14
large full-run archives (343451554 bytes) from the consolidated working tree.
Original Git objects remain. Current dependencies and small regression inputs are
retained separately. Root retention rules supersede older complete-run archive
recipes in component documentation.

Automatic approval review rejected the proposed original-checkout retirement and
metadata move. That action did not run. Originals remain recovery sources, with
agents paused; new implementation belongs in the consolidated directories. The
remaining prepared retirement is explicit, reversible via retained Git metadata
and preserved working snapshots, and requires renewed human disposition.
