# Current integration gates

Kernel, userland, sys-init and pkg-mgr now share this checkout. Work across their
interfaces locally; see [repository scope](../../docs/REPOSITORY.md) and root
[STATE](../../.planning/STATE.md) for the current implementation priority.

Maintainer decision, 2026-10-22: sys-init targets Aether only. Linux/BSD/illumos
product qualification and portability backends are retired, superseding decision
0153's deferral. POSIX authoring concepts and useful host regression checks remain.
Hosted CI is a development decision; its absence does not imply another OS target.

Current requirements are matched native contracts, safe owner initialization and
placement, filesystem-backed process/shell integration, and explicit shutdown/
export/reclaim evidence. Follow the [broker initialization handoff](BROKER-INITIALIZATION-HANDOFF.md)
and [filesystem boot contract](FILESYSTEM-BOOT-HANDOFF.md). Keep lifecycle policy
in sys-init, filesystem/runtime policy in userland, enforcing mechanisms in the
kernel and installation/trust in pkg-mgr. Directory co-location grants no authority.

Run focused checks for the affected boundary; [development checks](DEVELOPMENT-CHECKS.md)
explain the current-source host gate and separate historical/native audit. Actual
Aether execution, matched source identities and independent release review remain
required for corresponding claims. No standards pin, ABI or resource limit changes.

The [earlier gate chronology](archive/2026-10-22-integration-gates.md) is historical
reference, including withdrawn platform requirements and superseded native waits.
It is not a current instruction to pause or provision additional operating systems.
