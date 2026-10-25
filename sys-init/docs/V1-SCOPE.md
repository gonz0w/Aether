# Aether init v1

Maintainer scope update, 2026-10-22: Aether is the only product target.
Other-OS runtime support and qualification campaigns are retired, including
post-v1 portability goals. Host tools/tests and POSIX conventions remain useful.

Accepted by the maintainer on 2026-09-07: simple first, with broader features
shelved for a later release. This scope takes precedence over earlier roadmap
next steps and experiment follow-ons. Existing research is reusable evidence,
not a requirement to implement every explored mechanism.

## Finish line

Aether boots through sys-init into a usable environment with essential services.
A maintainer can understand the service configuration, see why a service failed,
observe a bounded restart policy, and request an orderly shutdown. Demonstrate
that sequence on one pinned Aether image using actual services, not only exit
workers. Select the available usable entry point with the Aether/userland owners;
do not claim a shell, login session or filesystem that has not been demonstrated.

V1 includes:

- One Aether boot path and a small, explicit set of essential services.
- Simple, inert service configuration: executable identity, required startup
  ordering and a bounded restart policy. Add readiness only where an essential
  service actually needs it; started and ready remain distinct.
- Supervision of service exit/failure, cleanup before replacement, fresh instance
  identity and a retry limit that prevents a crash loop. Normal completed cycles
  must not exhaust a lifetime six-record store.
- Predictable dependency failure behavior and orderly service shutdown in an
  explicit order. Unsupported kernel stop/power operations remain named blockers,
  not successful no-ops.
- Plain, useful failure/status diagnostics and a short build/run/configure guide.
- End-to-end boot, service failure/restart, retry exhaustion and shutdown checks;
  measured code/memory footprint on that workload, without speculative budgets.

## Short delivery plan

| Step | Deliverable | Done when |
| --- | --- | --- |
| 1. Simplify the implementation path (BG-063) | Map the v1 scenario to existing code; identify what to keep, simplify or leave experimental; select the smallest runtime/configuration path | A short code-level plan names exact missing mechanisms and the next implementation change |
| 2. Boot the useful baseline | Connect sys-init, configuration and essential service artifacts to the accepted Aether boot path | The pinned image reaches the selected usable entry point |
| 3. Finish supervision and shutdown | Add only missing restart, dependency and stop behavior for that baseline | Real services pass failure, cleanup, replacement, retry-limit and shutdown scenarios |
| 4. Make v1 reproducible and understandable | Consolidate the guide, scope, measurements and target acceptance | Another reader can build/run the baseline; actual release review gates are satisfied before publication |

These are delivery steps, not four equal-sized tasks or a calendar estimate.
The current result is still a prototype. Start with the source audit, not the
BG-062 checkpoint model. Use existing research; reopen a question only when the
v1 scenario requires it. Report a concrete missing companion mechanism when one
is found, and continue independent local work.

## Shelved for a later release

| Work | Backlog disposition |
| --- | --- |
| General completion archives, checkpointed cycle admission and long-term lifecycle history | BG-060 and BG-062 shelved; decision 0178 no longer selects the next implementation |
| General event/effect journal expansion and evidence-driven lifecycle framework | BG-057/BG-058 extensions shelved; audit existing enforcing checks for necessary v1 use |
| Supervisor replacement, durable state and crash/power-loss reconciliation | BG-031/BG-033/BG-051 broader recovery work shelved |
| Transactional package/service publication, rollback and configuration layering | BG-036/BG-037 broader integration shelved; v1 still needs exact service artifacts and simple configuration |
| Socket/timer activation, general device/mount/session management and advanced control protocols | BG-048/BG-049 and BG-050 extensions shelved; keep only operations required by the baseline |
| Additional OS qualification, expanded CI/stress infrastructure and broad conformance campaigns | BG-054 expansion and non-Aether work shelved; applicable local checks continue |

These items are deferred, not completed or discarded. They return only through
an explicit later-release scope decision, not automatically because an old story
says “next.” Mixed-scope stories retain useful v1 findings; this table governs
which portions are active. BG-056 quality work applies to actual changed surfaces
and release claims, not as a mandate to expand unrelated tooling before v1.

## Keep complexity under control

Every new runtime mechanism must explain which v1 acceptance scenario needs it.
Prefer direct lifecycle state and explicit ownership over a generic framework.
Retain evidence needed to resolve an outstanding operation; successful cleanup
does not by itself require indefinite raw history. Specify safe bounded state
reuse and stale-instance rejection without assuming the checkpoint architecture.
Do not weaken actual cleanup, authority checks or error handling to simplify code.

Preserve existing tests and immutable evidence while reviewing which experimental
paths belong in the product. No mass deletion, rewrite or language migration is
part of this scope change. Changes still follow CONTRIBUTING and scoped quality
checks; native behavior changes require fresh Aether acceptance. Shared standards,
release pins and cross-project authority remain unchanged. Other-OS runtime portability
is retired under the 2026-10-22 decision; Aether is the only product target.
