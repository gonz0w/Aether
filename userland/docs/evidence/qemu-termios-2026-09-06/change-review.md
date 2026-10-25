# UL-066/069 terminal translation diagnosis review

- Scope/requirements: diagnose reference cmspar failures without changing candidate,
  QEMU, test expectations or native interfaces. PLAN before runtime states three
  bounded private-PTY trace/readback cases and explicit restoration. Foundations E,
  CP/CD, TD/TE and local PX/TX evidence boundaries apply. Userland owns reference
  tools; no sibling changes or shared standard proposal is needed for this finding.
- Provenance: candidate hash checked against previous GNU build receipt. Image
  digest pins QEMU/coreutils/strace; their reported versions retained. Musl constant
  from original SDK retained, and build receipt retains its digest. Downloaded one
  upstream v10.0.11 GPL source file as research, hashed before local consumption;
  source notice preserved. This is not authenticated exact Debian source provenance.
- Authority/bounds: same owned offline non-root container with read-only repo,
  64 MiB scratch, 512 MiB/32 PIDs, 80-second outer budget, ten-second commands and
  15-second forced container cleanup. Three fresh PTYs, both descriptors closed.
  strace attaches only to the owned child commands. Explicit host tcsetattr restore
  measured independently on all cases. No user terminal, install or new SDK.
- Oracles/results: candidate set status 1 and host TCSETSW lacks CMSPAR; image set
  status 0 and includes CMSPAR; seeded host flag reaches host TCGETS but candidate
  reports -cmspar. Upstream cflag translation table omits the bit in both directions.
  Input header bit is 0x40000000. All three host restorations and container cleanup
  succeed. Readback distinguishes display loss from mere failed setter logic.
- Review/evidence: Codex task inspected trace bytes, helper versions, bit constant,
  both upstream translation calls and missing table entry. The browser's cached
  line numbers differ from downloaded source; retained bytes/hash are authoritative
  for this research snapshot. Independent source/reader and exact Debian patch
  review remain pending. No QEMU rebuilt/upgrade tested or general audit claimed.
- Documentation/follow-up: README, STATE, BACKLOG and draft coverage updated;
  UL-069 tracks isolated emulator source/patch provenance, CMSPAR set/read/clear,
  partial-failure and explicit restoration controls and full reruns. Do not waive
  failed parity cases. UL-066 remains active; native TTY, source trust, packaging
  and quality gaps remain UL-008/016/012/061–063. Prior evidence unchanged.
