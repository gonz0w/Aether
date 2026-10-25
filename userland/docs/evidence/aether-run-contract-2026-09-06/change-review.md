# UL-059 public contract review

- Scope: user-requested priority switch from UL-069 to UL-059. Specify public
  startup/result policy and handoff, not implement a CLI. Affected owners remain
  pending. Current runner, producer protocol, pins and exit-29 markers unchanged.
- Standards: pinned Experience COMMANDS/stream/authority rules, Foundations O/I/E,
  local Distribution/approved PD boundaries and documentation/TD/TE process.
  New shared requirements remain canonical Aether-standards work; this is local
  userland policy proposed for review, not a competing shared protocol.
- Design review: explicit argv boundary and byte limits, child argument ownership,
  environment default versus ambient propagation, atomic two-binding publication,
  no identity/name-derived grants, status/kind ambiguity, finite observation,
  unknown-result no-replay and separate cleanup evidence. Parent startup capacity
  differs from child capacity; producer fixed startup/29 cannot be silently reused.
- Presentation review: help/version stdout, errors only on granted stderr, child
  stdout unmodified. No color/animation/format flags advertised without support.
  Existing 64-byte file does not establish native help capacity. Runner-owned
  exits follow 0/1/2/64; inherited child statuses preserved. No 125/126/127 exception
  is declared. Earlier proposals remain historical, and owner agreement pending.
- Acceptance: fourteen explicit public-CLI cases, all NOT RUN. Existing native
  nine-case evidence remains scoped to old runner. No behavior source changed,
  so no unrelated native tests rerun. Run local quality and standards adoption
  checks for documentation links/pins/inventory, not runtime conformance.
- Documentation: contract in docs/AETHER-RUN.md, architecture link, roadmap
  acceptance pointer, backlog/STATE priority and runner README navigation; draft
  coverage entry added. Exact reviewed current owner docs and finite runner source
  snapshot hashes retained. Intent/project goals unchanged.
- Actual review: Codex task technical reading of current contracts and source,
  startup/status conflicts and owner boundary. No independent reader, affected
  producer/pkg-mgr/sys-init sign-off or sibling messages. UL-059 stays active.
  Next owner review plus UL-063 source audit before implementation; UL-058 and
  full CR-01 remain incomplete. UL-069 evidence retained for later resumption.
