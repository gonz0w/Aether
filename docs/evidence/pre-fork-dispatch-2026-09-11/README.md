# Requests before fork and explicit owner capacity — 2026-09-11

The parent can query for children and perform file I/O before its first fork.
The selected workload gets ECHILD without changing its status buffer, denies a
foreign-reference read without publishing a byte, and reads a. Its copied child
executes /next and reads b; the parent collects the actual exit 72 and reads c.
Positions, holders, CLOEXEC, mask and identity checks survive the phase transition.
Two generations require three backend closes each and six reclaims. This remains
a private producer composition client, not actual dash or installed SDK acceptance.

The measured owner needs more than the old 8 KiB fixture allowance. AENMX002 / ABI17
explicitly permits up to 16 KiB of supervisor code; AENMX001 / ABI9 retains its old
8 KiB limit. Header layout, ELF limits, channel/worker counts, capabilities and the
one-page supervisor stack are unchanged. Existing loader mapping logic allocates
only required code pages and verifies RX code, RO/NX aliases, RW/NX stack and zero
tail. Native 16,383/16,384-byte images pass. Downgrade to the old version and an
oversized 16,385-byte envelope reject before any worker is admitted. Host tests
cover both versions' size, reserved-byte and length boundaries.

All 223 connections cases, five launch cases, 23 init-large cases and 32 init-composed
cases pass, together with host tests and format/pin/workflow checks. The pre-fork
-wait and -foreign controls require parent86/owner1950/reclaimed0 before child
admission; a generic panic or timeout is insufficient. The older init tests retain
code-write, stack-execute and dirty-tail rejection coverage for the shared mapping
checks. The new owner capacity does not publish a new syscall or grant.

Attempt1 passed host/launch but failed the unchanged 8 KiB owner link assertion
before connections boots. size-diagnostics preserves three build-only sharing
probes; two failed the original linker, and a temporary measurement-only linker
measured 10,152 bytes. None was booted. Exact start/durations were not recorded for
those diagnostics. The unsuccessful sharing attributes were removed. A later
editing helper assertion is recorded separately. Attempt2 passed host but launch
and connections builds failed before QEMU because code_pages was out of scope in
the existing init diagnostic after sharing validation. The final run fixes that
scope and qualifies both existing init-capacity profiles as well as connections.
All attempt inputs, logs and artifacts are retained.

The pre-code requirement and SE-01–SE-05 review are in NATIVE-SHELL-STARTUP.md,
including the capacity refinement prompted by measured failure. Reusing one file
handler and position array removes a request-order assumption without another
service. A separate versioned format preserves old consumers. No new unsafe/FFI
boundary, dependency, sibling change, installed SDK update or released-pin change
is made. Backend exchanges and pre-fork receives remain bounded and synchronous;
post-fork client polling remains incremental. Stable valid pointers, one caller
context, fixed /next authority and one fork remain explicit limits.

Ordinary dash external commands use vfork; a subshell uses fork and wait3. This
packet does not run either actual shell path. Next compose actual startup services
and a reviewed fork-based command candidate, then obtain matching SDK/consumer
acceptance. General pre-fork writes, other wait selectors/options, close-before-fork,
quota exhaustion, live-signal composition, arbitrary path/pointer handling,
persistent loading and full-shell/R1 acceptance are not established. No independent
owner or reader approval is claimed.

run-sources binds frozen execution inputs; sources adds final documentation. The
source and artifact archives are read back against hashes. compatibility.json
compares all 216 prior cases: kernel bytes intentionally change for the new format,
and all older cases must still pass on that kernel. The shared ABI tuple check changes210 older owner binaries; all worker ELF bytes
and other header fields remain identical outside developer entropy and owner length.
The initial narrower comparison assumption is retained in collection-attempt1.json
and collect-attempt1.py; component inspection and common-entry prefix bytes explain
the difference. The representative size-optimized entry uses48 extra stack bytes
for its expected ABI/grant tuple; the existing one-page stack allowance is unchanged. owner-sizes.json verifies format-specific
bounds and absence of admission for the two malformed new envelopes. qualification
and timing records bind commands, counts and sizes. final-checks.json records host,
format, workflow, standards and whitespace results. collect.py verifies the prior
sealed packet and the four-file simplicity snapshot. manifest.json seals this
packet. Reproduce using the recorded SDK/tool paths and the commands in the native
connections reference; archived outputs can be restored to their recorded paths.

cleanup.json records removal of exact archive-verified superseded unpacked outputs
after open-file checks. Current connections, launch and both init-capacity outputs
remain unpacked; retained archives preserve accepted and failed evidence.

The first final-document check found one trailing space in the new reference;
final-checks-attempt1.json retains that failure. It was removed before sealing.

Final totals: 242 source inputs, 4,606 target artifacts,
maximum compiled owner 8,328 bytes and maximum accepted
envelope owner 16,384 bytes. Cleanup removed six verified
superseded unpacked directories (2.58 GiB); the four final
profile directories in qualification.json remain available.
