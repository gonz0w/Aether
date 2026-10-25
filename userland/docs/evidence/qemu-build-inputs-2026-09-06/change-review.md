# UL-069 build-input review

- Requirement/scope: prepare pinned inputs for isolated QEMU/Clang build. PLAN
  precedes acquisition. No emulator compiled/patched, dependencies installed,
  native interface changed, sibling edited or prior runtime image modified.
- Applicable rules: Foundations E, approved CP/CD/TD/TE, local licensing and quality
  process. Build tooling remains userland-owned; upstream files preserve GPL and
  package payload terms. Full dependency license review remains before shipping.
- Ownership/bounds: read-only prerequisite probe in existing image, then two owned
  download-only containers. 240-second acquisition deadline, 2 GiB/128 PIDs,
  cap-drop=all/no-new-privileges, private build output bind, 15-second owned cleanup.
  Network used only to acquire repository metadata/packages; no authentication
  bypass. Source download bounded at 120 seconds. All three containers cleaned up.
- Attempts: first apt run status 100 due missing user-switch authority/permissions;
  retained unchanged. Retry keeps capabilities disabled and uses root sandbox user
  with private apt directories; status 0, all 103 package hashes verified. Root is
  inside the collector, not host root. Download-only does not execute maintainer
  scripts. Existing apt cleanup hook warning is retained and not a runtime pass.
- Pins/provenance: exact apt package versions, every collected file hash, signed
  metadata and sources config retained. Release archive hash verified before
  selected source review. HTTPS source trust is still UL-016. Build lock records
  absolute local artifact paths; all bytes remain under build and must not be
  pruned. This evidence bundle holds logs/receipts, not duplicate package archives.
- Review/tests: Codex task inspected prerequisites, source build Python requirements,
  target CMSPAR definition, apt statuses/authentication behavior, package inventory,
  hashes and cleanup. Current QEMU documentation is a research lead; actual release
  bytes are the pinned build input. Independent source/reader/build review pending.
  Hash checks establish retained byte identity, not build reproducibility/security.
- Next/acceptance: offline isolated install/build with explicit Clang, baseline and
  patched emulator comparison, exact tool/library identities, parity/recovery and
  full consumer reruns. UL-069 active; UL-066 still incomplete. No native Aether,
  full POSIX, performance, source-security or release acceptance claim.
