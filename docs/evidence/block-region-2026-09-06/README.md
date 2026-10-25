# Bounded disk-region evidence — 2026-09-06

[Native block v2](../../NATIVE-BLOCK.md) passes on frozen final sources.
AENBD002 / ABI 14 adds bounded region transfer and metadata query to the existing
caller/generation-bound block grant. Kernel validation copies the entire request
before committing scalar authority and checks the complete output span before
writing metadata. Sector addressing is relative to the delegated region.

## Final checks

`block-region-final-2026-09-06/results.json` records exact commands, UTC intervals
and successful exits for the selected suites:

- Five region cases using a 16-MiB disk and 8-MiB region starting at sector 8.
  Relative sectors 0, 777 and 16383 are seeded, written/flushed, and read in a fresh
  VM. The host compares every disk byte, including both sides of the region.
- Read-only attenuation, malformed region records, overflow/past-end bounds,
  invalid metadata spans, stale/terminal targets, failed-transfer ownership,
  copied request scalars, onward-transfer denial and permanent close.
- Actual recipient #UD fault (generation 2, kind 2/detail 134) followed by a new
  generation denied query and I/O. The fault occurs without an explicit close.
- Five unchanged v1 native cases, seven hardware cases, two console-relay cases,
  seven M4 cases, and one-core boot/framebuffer smoke.
- Host tests (85 Python cases plus kernel checks), offline standards/workflow,
  scoped Zig/Rust/C formatting and Experience validation.

## Attempts and triage

- `block-d3rdmpqd`: build failure, no guest cases run. Zig rejected a local `start`
  shadowing the existing entry function. Renamed it `region_start`; no runtime
  failure or infrastructure error was involved.
- `block-5c8rsy_s`: corrected initial five-case region pass.
- `block-c4ixc2ew`: intentional negative control. Omitting only the delegated
  physical base makes the first region read return incorrect seed bytes. The
  unchanged positive oracle rejects at supervisor 841/reclaimed 1 with the exact
  native-profile panic. This is an expected product mutation failure, not a
  successful target suite. Later cases were not run. The wrapper restored source
  in `finally`; its assertion and exit receipt are retained.
- `block-85hrjuu2`: final five-case region pass after restoring the implementation
  and correcting the block-handler comment. The final wrapper also reruns all
  selected older profiles on these bytes.

Each attempt retains its original report, exact source archive and generated
artifacts/logs, including failed build inputs. Source archive members were checked
against every receipt digest. The final source hashes were also compared with the
working source tree. Additional regression archives, the one-core ISO, command
wrappers and documentation snapshot are retained alongside them. SHA256SUMS covers
this evidence tree except the manifest itself.

## Scope and remaining gates

No sibling implementation, consumer pin, shared standard or dependency changed.
The Rust supervisor and C client are conformance fixtures, not a filesystem service.
The profile remains synchronous, BSP-only and fail-closed on device uncertainty;
DMA storage is retained on failure. VM-restart persistence does not prove power-loss
durability. Filesystem-engine integration, consumer review, production adoption,
async progress, device-error recovery, physical targets and assembled R1 release
acceptance remain unproven. Existing missing extended-runner and independent-review
coverage in DEVELOPMENT remains open.
