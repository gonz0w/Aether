# Boot stages and configuration layout

Date: 2026-09-05. Research handoff for BG-003 and BG-014. Candidate semantics and paths only; no architecture decision, target boot implementation or filesystem ABI is accepted here.

Recommend a small lifecycle vocabulary with named service profiles, plus separate storage classes for package definitions, operator policy and runtime observations. Boot phases describe progress; profiles describe desired service sets. Neither should conceal readiness requirements or grant authority.

## Comparative evidence

| Source | Observed model | Implication for our proposal |
| --- | --- | --- |
| [runit](https://smarden.org/runit/) | Three stages cover initialization, supervised operation and shutdown; stage 1 can provide an emergency shell. | Keep the outer lifecycle understandable; a stage boundary does not need a rich target object. |
| [OpenRC user guide](https://github.com/OpenRC/openrc/blob/master/user-guide.md) | Named runlevels group services, with sysinit/boot/default sequencing and separate enablement from start. Its guide contrasts names with traditional numeric runlevels. | Prefer named profiles to opaque numbers. Do not equate profile membership with a running service. |
| [FreeBSD boot handbook](https://docs.freebsd.org/en/books/handbook/boot/) | Kernel hands off to init; single-user repair precedes normal multi-user configuration. Console policy affects access. | Make repair entry and its authority explicit; do not assume Aether has a shell, Unix root, or the same console trust. |
| [systemd bootup manual source](https://raw.githubusercontent.com/systemd/systemd/main/man/bootup.xml) | Dependencies connect initialization, mounts, services and normal/rescue/emergency targets. | Express real prerequisites, but avoid importing the full target vocabulary or Linux facilities. |
| [illumos restarter manual](https://raw.githubusercontent.com/illumos/illumos-gate/master/usr/src/man/man8/svc.startd.8) | Milestones select service scope; the restarter manages dependency and failure state. | Report whether desired scope was reached, with reasons when it was not. |
| [s6 service directories](https://skarnet.org/software/s6/servicedir.html) | Configuration can be read-only, while supervision/event directories need writable storage; copying a service image into runtime storage is a documented approach. | Separate authoritative definitions from live machinery; do not introduce boot-critical dangling-link dependencies. |
| [FHS /run](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch03s15.html), [FHS /var/lib](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch05s08.html) | Runtime information and persistent variable state serve different purposes. | Use these familiar distinctions for a POSIX host profile, without claiming FHS is POSIX or binding Aether to it. |

Sources consulted 2026-09-05. These are primary project manuals and FHS 3.0; moving source branches are documentary evidence, not tested release behavior. Earlier [boundary](BOUNDARY-HANDOFF.md) and [package](PACKAGE-SERVICE-CONTRACT.md) findings provide the ownership and validation constraints.

## Candidate lifecycle and profile vocabulary

| Candidate phase | Entry / completion meaning | Failure behavior |
| --- | --- | --- |
| `bootstrap` | Receive a supported launch context, authority, initial configuration and diagnostic route | Invalid context prevents normal activation; recovery may require the upstream bootstrap owner |
| `prepare` | Validate effective configuration and establish the minimum resources needed for the selected profile | Keep control/diagnostics available where possible; required resource failure prevents profile completion |
| `activate` | Start the selected graph as prerequisites are satisfied | Required dependency/readiness failures block affected work; independent optional work follows explicit policy |
| `operate` | Initial required profile obligations have been satisfied; continue observation and lifecycle requests | Later failures change current satisfaction/health, rather than falsifying the recorded initial boot result |
| `shutdown` | Stop accepting new activation, resolve in-flight actions, stop required work, release resources and request platform halt/reboot | Failed or unknown stop/release prevents a successful shutdown claim; final handoff failure remains visible |

`rescue` is a candidate recovery mode reachable when its own prerequisites and authority are available; it is not a promise that every failure can spawn a shell. Minimal diagnostics may be all that is possible before bootstrap succeeds. A normal runtime must never discard its process/task ownership merely because it entered rescue.

Candidate profiles: `normal` for the configured service set, and `maintenance` for a minimal authorized repair environment. Conventional `multi-user` and `single-user` can be compatibility/UI labels only after login and shell facilities exist. Graphical, networked, installer or other profiles should be added for real use cases; no fixed numbered runlevels are required by this research.

These are names for later specification (BG-038), not command syntax. No profile grants root or capabilities. The first native experiment may have only one fixed service profile and diagnostic output.

## Transition rules to specify

- Freeze the effective definition/enablement generation for an activation attempt. Report later configuration changes as pending rather than silently changing the graph in flight.
- A successful one-shot satisfies only its declared completion obligation. A long-running dependency requiring readiness cannot be released merely because its task was launched.
- Optional failure may permit a degraded outcome only when the profile says so; required failure leaves the profile unsatisfied. Expose failed service, missing prerequisite and chosen policy.
- Profile switching requires an explicit start/stop plan, including services started outside the profile. Do not infer permission to stop arbitrary work from a profile name.
- Returning from maintenance to normal validates again and resumes/reconciles explicitly. Do not replay successful non-idempotent setup jobs blindly.
- A package update changes configuration through the package/service protocol; it is not a new boot phase and does not automatically rerun preparation scripts.
- Shutdown must consider actual running instances and in-flight jobs, not only the latest desired graph. Readiness/dependency edges and stop ordering are not automatically identical. BG-024 must define reverse ordering, cycles during shutdown, timeouts and forced teardown.

Illustrative trace: bootstrap succeeds; runtime storage is available; a logger becomes ready; an application needing that logger starts. If the logger cannot satisfy a required readiness condition, report the application blocked. Enter maintenance only if its diagnostic/authority prerequisites work. A missing shell must be reported as missing recovery capability, not followed by an assumed successful rescue transition.

## Candidate storage layout

The paths below are a POSIX-host/distribution proposal. They are not created by this work, and native Aether objects may initially have no filesystem representation.

| Content | Candidate host path | Ownership / availability |
| --- | --- | --- |
| Vendor service descriptions and profile definitions | `/usr/lib/sys-init/` | Package-owned, immutable during an activation attempt; schema/layout versioned |
| Local overrides and enablement/profile policy | `/etc/sys-init/` | Administrator-owned; kept distinct from vendor defaults |
| Runtime status, endpoint discovery and operation observations | `/run/sys-init/` | Volatile; scoped to boot/instance identity; reconstruct or mark unknown after restart |
| Durable coordinator/state records, if justified | `/var/lib/sys-init/` | Defined writer and recovery protocol; never assume persistence is required for all runtime state |
| Persistent diagnostics, if configured | `/var/log/sys-init/` | Separate retention policy; unavailable logging must not silently wedge boot/control |
| Disposable derived validation cache, if useful | `/var/cache/sys-init/` | Rebuildable; never authoritative or required for rescue |
| Minimal bootstrap/recovery configuration | Boot-supplied bundle or a separately specified early path | Must be available before the resources it repairs; exact image/path contract waits on Aether |

No symlink-based enabled tree is required. Compare links, a bounded text set, and profile membership data in BG-039/BG-037. pkg-mgr's current staged-state contract rejects links and lacks mode/ownership metadata, so a link-heavy runtime scheme cannot be presumed packageable. Keep installed payload and runtime-generated entries separate even if a host adapter ultimately uses links.

All enabled definitions and recovery dependencies must be reachable before use. If `/usr` is separate or unavailable, a normal vendor tree there cannot bootstrap its own mount. Options are an early immutable bundle or an explicitly required available root containing the needed definitions and executables. Choose this after the target image contract; do not hide it behind a directory convention.

Early diagnostics may buffer in bounded memory or use an available authorized channel; neither /var nor a graphical service is a universal prerequisite. If /var is missing, volatile operation may continue only under declared policy; durable updates must fail/defer. A read-only root should be possible when writable runtime storage is independently available.

Cache/status files from a previous boot are not proof that a service exists. Directory names and hashes do not grant runtime authority. Namespace, permissions, traversal/link handling, maximum sizes and ownership must be specified before any privileged reader/writer is implemented.

Migration proposal: version the layout/descriptor profile, prepare and validate the new effective view, preserve operator overrides/disable intent, and switch only under a defined publication protocol. Never merge vendor updates into administrator files silently or delete application data during layout migration. BG-039 defines compatibility; BG-036/BG-031 define publication/durability.

## Companion refresh and target gate

At this review, [Aether STATE](../../../.planning/STATE.md) reports M3 complete and M4 next: a separate display-service image and supervised cross-core worker restart. [Aether PROJECT](../../../.planning/PROJECT.md) explicitly keeps POSIX/libc, filesystem and networking outside its POC requirements. Its [Limine configuration](../../../boot/limine.conf) loads a kernel and fixed protection module; that is not a sys-init service schema.

[pkg-mgr STATE](../../../pkg-mgr/.planning/STATE.md) now reports a staged kernel/module pair consumed by Aether's image builder and a successful older SMP IPC smoke marker. Its [boot handoff](../../../pkg-mgr/docs/AETHER-HANDOFF.md) is artifact transport and explicitly marks service activation unsupported. Its [service proposal](../../../pkg-mgr/docs/SERVICE-HANDOFF.md) agrees on separating ownership, enablement and live state; its references to BG-027 being pending are stale relative to our completed research, while the absence of a validator remains accurate. These companion results were read, not rerun, and the older smoke marker is not evidence for Aether's newer M3 acceptance.

The following target work should wait; no further paper API should be treated as a substitute:

| Blocked target work | Concrete evidence needed to resume | Existing owner/story |
| --- | --- | --- |
| Launch sys-init as a native service | A documented accepted image/launch seam, ABI and initial grants usable by a sys-init-owned component | Aether + BG-033/BG-034 |
| Reliable native supervision and restart | Instance identity, terminal observation and stop/reclaim semantics for that seam; supported polling/event and timeout limits | Aether + BG-032/BG-028 |
| Native rescue and final shutdown | Available diagnostic/control authority, supervisor-failure policy and explicit platform shutdown behavior | Aether + BG-033/BG-024 |
| Native installed service layout | Accepted boot/configuration source and target filesystem/image ownership contract | Aether + pkg-mgr + BG-039/BG-035 |

M4 completion by itself is not the gate: inspect the actual exposed interfaces. Static fixed-image operation may satisfy a bounded experiment without a general loader, but must be agreed explicitly. No background polling, companion modification or scheduled wakeup is established by this handoff.

Independent work remains useful: readiness semantics, state-machine examples, descriptor validation research and host failure fixtures after decisions. We can pause native implementation while continuing those bounded tasks.

## Completion and future verification

BG-003's comparative boot research and BG-014's layout proposal are complete as research. BG-038 captures exact phase/profile transitions and boot-trace fixtures; BG-039 captures layout, early-bundle and migration specification. Existing BG-028/BG-034 carry prototypes, BG-037 carries enablement, and BG-036 carries package publication; no separate prototype script backlog is needed until the execution profile is defined.

Future fixtures must cover required/optional readiness failure, maintenance without shell, repeated setup, interrupted profile switch, shutdown with in-flight actions, read-only root, missing /usr or /var, stale runtime state, invalid overrides, link/traversal rejection, failed migration and preserved administrator intent. Host simulations cannot establish Aether bootstrap/recovery or filesystem durability.

Next independent item: BG-007/BG-022 readiness and health semantics. Target implementation remains gated as above. Source observation hashes are recorded in [the local manifest](BOOT-LAYOUT-SOURCES.json); no runtime implementation or benchmark was produced.
