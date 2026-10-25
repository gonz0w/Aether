# Working on the experimental POC

> Public consumer routing: apply [PROJECT's cutover rule](../PROJECT.md#public-onboarding-cutover).
> After verified onboarding/migration, “canonical work record” in this guide means
> the owning GitHub issue. STATE is navigation and legacy queues are read-only.
> Before cutover, only the approved bootstrap record owns onboarding. Execution,
> review, source-freeze, resource and acceptance requirements below stay binding.
> Local qualification receipts and the whole RC1/ADP-01 packet are excluded from
> this snapshot; required missing evidence remains blocked coverage.


Start with the root [README](../README.md) for pinned setup and
[AGENTS](../AGENTS.md) for project boundaries. Read root [PROJECT](../PROJECT.md)
and the pinned [Agent Temper method](../.agent-temper/METHOD.md), then apply
PROJECT cutover policy and read the canonical issue and discussion. Root STATE
is compatibility navigation.
Confirm its finite scope, readiness and authorization before implementation.
ROADMAP capability gates and historical next-action notes are not assignments.
`docs/archive/` contains superseded plans, not implementation requirements. Shared
Aether standards and their release/review bytes remain private. Consumer adoption
records and lock identities remain here, without those offline inputs. See
[PUBLIC-SOURCE](PUBLIC-SOURCE.md) before selecting checks. Ordinary public prose
and self-contained model work do not require private clauses; affected normative
changes require the owner and exact inputs before dependent implementation.

Follow [the development workflow](DEVELOPMENT.md) for required test selection,
standards review, source conventions and evidence retention.

Select checks under [the focused test cadence](DEVELOPMENT.md#test-selection-and-cadence)
and record them in the canonical work record. Documentation-only changes use
documentation checks. The following are broad checkpoint commands, used only when
the selected scope requires them and applicable native-execution approval is valid.
These broad gates need private standards/local inputs and remain blocked when
those are unavailable. Dependency setup alone does not supply them. When all
required inputs and approval are present, run from the repository root:

```sh
zig build test
python3 scripts/regression.py
```

The regression builds seven images into a fresh `zig-out/regression-*` directory.
The positive image must produce the exact `AETHER FAULT RECOVERY PASS` line and
pass framebuffer pixel checks. Five negative images must emit these exact panic
reasons:

| Build flag | Required panic reason |
| --- | --- |
| `skip-remote-unmap` | `remote stale mapping retained` |
| `skip-remote-zero` | `remote code not cleared` |
| `skip-remote-discard` | `remote transport not drained` |
| `drop-remote-terminal` | `SMP supervisor fault; resources reserved`, with ordered context below |
| `bad-stream-generation` | `display service checks failed`, with replacement context below |

The terminal case must first record `REMOTE: AP confirmed stopped, unmapped and
zeroed backing`, then `REMOTE: unsolicited AP user fault retained (#UD)`, then
the exact supervisor panic. These existing lines establish progression through
the first cleanup into the next faulting generation; a supervisor fault before
that progression is rejected. No new guest diagnostic or ABI is introduced.

The stale-generation case tags sequence 21 as generation 1. It must record the
first remote cleanup, then `DISPLAY: second-generation result rejected after 20
acknowledgments`, then the exact display panic. The diagnostic requires the
fixture's validation-failure status plus kernel-owned counts (20 sends, 21
receives) and a live generation-2 endpoint namespace. This identifies the bounded
replacement experiment; it does not authenticate arbitrary user reports or prove
recovery from a general display failure. The user-space service validates the
payload. An unrelated display panic cannot satisfy the oracle.

The pixel-negative image, `skip-display-draw`, must reach exact successful guest completion,
produce a complete 800x600 P6 capture, and fail a pixel comparison. It uses the
PPM capture during validation. Missing/truncated/malformed captures, panic, timeout,
or correct pixels cannot satisfy this test. The normal image still requires correct pixels.

A failed build, missing tool, unexpected panic, early QEMU exit, unexpected guest
success in a panic case, or timeout fails the suite. A nonzero exit alone is never
negative-test evidence. Builds have a 180-second bound per case; guest boot has a
30-second bound. QEMU is stopped after each case, with private firmware variables.
Each case retains compact build and emulator logs; generated images and captures
are removed after the run under [the retention policy](DEVELOPMENT.md#evidence-and-failures).
`results.json` records exact build commands, input file digests,
image and passing serial-log digests, ordered panic context, pixel-negative
expectations, and case outcomes. Interrupted/failed runs
remain incomplete. These are current-working-tree witnesses, not independent
clean-checkout reproduction, source authenticity, network confinement, or a full
release evidence bundle. Do not change sources during a run or share its output
prefix with another emulator. Read failures in that run's case directory; rerun
after fixing the cause and confirming any required native authorization. Retain
each attempt's compact result and failure summary under
[the evidence policy](DEVELOPMENT.md#evidence-and-failures); do not retain complete
run directories, generated captures, images or source trees.

The script provides `--help` and `--version`, emits plain ASCII output, and needs
no interactive answers. Exit codes: 0 all cases passed; 1 operational/test
failure; 64 invalid usage; 130 keyboard cancellation. Existing build and emulator
commands keep their exit contracts. Run `zig build smoke -Dsmp=false` separately
when changing the lifecycle v1 seam; native C has its own documented harness.

Small candidate starter ideas are listed below. They are not authorized work.
Check canonical Issues for existing ownership and completion after cutover, then scope any selected idea
in a canonical bounded record with acceptance, checks and required authorization
before implementing; preserve its stable ID when one already exists.

| Task | Boundary and acceptance oracle |
| --- | --- |
| Regression evidence completeness | Bind framebuffer checks and test inputs to compact case evidence; missing or changed inputs must be reported explicitly. Preserve existing result fields and compact retention, and avoid claiming source authenticity. |
| Framebuffer capture parser | Add format/bounds cases around the actual QMP P6 profile. A malformed capture must remain a harness failure even in the pixel-negative mode. Avoid expanding format support without a consumer. |
| Independent checkout witness | After the maintainer prepares a committed candidate, run documented setup/reproduction independently and retain its source revision, tool versions and target results. A working-tree snapshot alone does not close this gate. |

Changes should explain the concrete problem, affected producer/consumer,
compatibility, tests and remaining limitations in their canonical work record.
Follow [PROJECT's integration policy](../PROJECT.md): required checks and separate
review precede agent integration of accepted work. Authority and shared ABI changes
need affected-owner review; native approvals and release gates remain separate.
Do not invent sign-off. Keep sys-init supervision policy and pkg-mgr installation
policy in their owning components.

Original contributions are offered under [BSD-2-Clause](../LICENSE); contributors
retain copyright. See the [consumer licensing summary](LICENSING.md).
Before distribution, review third-party obligations and verify the private
GitHub reporting route in [SECURITY](../SECURITY.md). This license decision promises no security support. Do not submit secrets through
public issues. These decisions do not block local engineering.

## Source reproduction

When the selected work requires source reproduction and applicable native approval
is valid, run `python3 scripts/reproduce.py` from the repository root after pinned
setup and the exact private standards/local inputs selected by its contract.
This broad host/target run is blocked without those inputs and is not a routine
documentation check.
It copies current sources, host tests and offline standards into a fresh
`/tmp/aether-reproduce-*` directory. It excludes `.git`, historical archives,
retained evidence, generated outputs and all existing Zig caches. It separately
copies and verifies the already-fetched boot dependencies. It runs host checks,
the seven-case target regression, and one-core lifecycle v1 smoke, with both Zig
cache paths inside the new snapshot. Cases within the run can reuse that new
cache. No sibling checkout is copied or required by these commands.

The retained `results.json` identifies copied source and dependency bytes,
installed tool versions and executable locations, host architecture, commands,
outcomes and generated artifact digests. Compact logs identify each step. Generated
source, dependency, build/cache trees and framebuffer captures are not retained
after completion, including failure. Each top-level step has a 900-second timeout;
existing regression build/guest timeouts remain.
Sources must remain stable during snapshot creation. Copied sources and dependency
bytes are checked again after successful execution. Inspect compact results and
logs in the printed directory on failure, including any cleanup failure. Link the
attempt from the canonical work record and follow
[the retention policy](DEVELOPMENT.md#evidence-and-failures); do not create a
replacement source archive.

`--help`, `--version` and exit codes match the regression script. This is local
source-snapshot reproduction with fresh caches. It does not establish an
independent committed-checkout witness, bit-identical builds, fresh installation
of the host toolchain, authenticated inputs, or enforced network confinement.
Native C and companion suites remain separate acceptance scopes.
