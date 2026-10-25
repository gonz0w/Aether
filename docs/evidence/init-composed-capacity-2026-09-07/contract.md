# SI-06 producer contract before implementation

Allocate AENIN003 / ABI 16, opt-in --init-composed, with the unchanged 56-byte
two-ELF envelope and 1..16384 supervisor code bytes. Preserve v1/v2 byte limits,
identifiers, grants, worker slots and lifecycle behavior. Code maps RX at
0x400000 through at most 0x403fff; every kernel alias remains RO/NX. Check lengths,
reserved fields, zero tail and mappings before entry. Existing 128-page backing
capacity already accommodates four code pages and one stack; no quota increase.
Stack stays one RW/NX page at 0x800000 with initial RSP 0x800ff8. More code does
not prove composed stack fit. Normal success halts; owner exit/fault performs the
existing verified whole-domain cleanup. New ASCII COMPOSED PASS/CLOSED and mapping
markers are confined to v3. Existing emergency/machine markers remain unchanged.

Required tests: all added code pages execute, below/at/above code limits, old-profile
oversize rejection, malformed/truncated/extra/overflow lengths, zero tails and
dirty-tail control, writes to added code pages denied, stack execute and guard
faults, normal lifecycle and owner-closed cleanup. Run v1/v2, shared loader/profile,
thread/memory and M4 regressions plus host/pin/format checks on frozen final sources.
Retain all attempts and complete source, boot inputs, SDK/tools and raw artifacts
for independent sys-init consumption. Inspect its retained composed candidate
separately; consumer Terminal semantics/stack acceptance remain independently owned.
No sibling edits, pin changes, new workers or authority, recovery or Cleaned policy.
Foundations O/I/E, local DEVELOPMENT/TD/TE and Experience machine-marker exception
apply. Existing Python compact style remains scoped; no whole-harness reformat.
