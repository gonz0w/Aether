# Native SDK error guards — 2026-10-04

UL-003/015/081. The maintained native-C recipe now checks two reproduced musl1.2.6
provider failures. Realtime fallback returns the actual gettimeofday error before
conversion/success. Physical/available-page sysconf checks __lsysinfo before reading
its structure. Exact upstream hashes/anchors and before/after patches are recorded.
Only clock_gettime.lo and sysconf.lo differ across the old/new libc archives.

Three fresh native VM cases pass: corrected SDK with real unsupported providers,
old SDK clock rejection240, old SDK physical-page rejection241. Each has two exact
isolated terminal results. The fixed case also completes unchanged native memory/
startup behavior with24 output bytes per context and the kernel acceptance marker.
Private replacement-source provider controls exercise ENOSYS/EACCES/EINTR,
unchanged failed clock buffers, exact call counts, primary success, realtime
fallback microsecond conversion, page-unit success and unit-zero fallback. These
are injected providers, not native time/capacity delivery. Monotonic error mapping,
other sysconf branches, arithmetic overflow and concurrent/interrupted scheduling
are not newly qualified. No missing semantics are implemented as success.

[Qualification](qualification.json) binds ELF/ISO/library identities and boot-module
readback. Generated boot.catalog metadata changes with ISO replay; all other
boot modules except the selected native-C envelope remain byte-exact. Static
links have no external undefined symbols or Linux syscall sites. Original Aether
producer manifest was completely verified before its baseline archive was read.
No sibling build or source mutation is performed.

[Candidate delivery](delivery.json) provides clean staged SDK, original source
archive/notices, modified units, frozen maintained recipe, tool pins and patch/
build receipts. Every delivery archive member is independently read back against
its selected seal. Existing SDK pins, old SDKs, userland runtime and shell kits
remain unchanged. Independent Aether consumption/acceptance stays pending; the
candidate does not supply real clocks, entropy, identity, engine resources or I/O.

Retained attempts: the completed SDK build was followed by a local JSON adapter
TypeError (CompletedProcess is not JSON-serializable); its authoritative bounded
build receipt passes. Initial probe compilation lacked feature macros and the
initial local adapter did not check returned exits; both logs and initial source
remain. Checked second adapter compiles/runs successfully. Initial full-ISO parity
expectation rejected generated boot.catalog changes; the scoped module check
retains and explains that metadata difference. No failed attempt counts as a pass.

[Source review](source-review.md) records scope, ownership, plan and remaining
review. Runtime commands use the unchanged owned process helper;35-second guest
and45-second outer bounds,1MiB UART/4MiB QEMU stderr; fresh firmware and complete
emulator/group reap. All attempts and exact commands/sources are retained in the
private evidence archive. Quality/syntax/whitespace results are retained separately.
Musl notices and original BSD-2-Clause recipe licensing remain distinct.
