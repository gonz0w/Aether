# Composed init and Terminal consumer — 2026-09-07

Decision 0175 independently accepts AENIN003/ABI 16 for the bounded native
Terminal experiment. The producer packet matches its manifest; all 499 source
files match the archived map. A consumer-owned intake receipt preserves the
original producer source/report/envelope bytes and provenance. No sibling file,
shared release pin, old envelope or old evidence was changed.

All 214 sys-init cases pass in fresh Aether QEMU execution from captured sources,
including the generated-dependent Terminal positive (100/reclaimed 3) and five
controls (1094–1098/reclaimed 0). An independent source-extracted replay also
passes all 32 producer composed-profile boundary cases using pinned SDK libc.
Those cases cover page/length boundaries, malformed inputs, code-write and
stack-execute denial, stack guards, dirty-tail rejection and owner cleanup.
This replay rebuilds helpers and kernel, not libc. The 453 upstream cases remain
producer evidence; they are not counted as our executions.

The Terminal session binds the original owner, generated worker and retained
launch acknowledgment before observe/status/observe. Its exclusive borrows keep
the association stable through sampling/application. Actual raw returns are
retained before interpretation. Wrong-owner and premature application deny;
missing/corrupt reclaim capture retains Unknown and closes admission. Local
interruption preserves the two completed reads and prevents further capture or
application. Exact repeat application cannot issue another effect.

The positive image is 11,680 bytes within the explicit 16,384-byte limit. All six
new paths execute with the unchanged 4 KiB stack and no guest fault. This is
bounded path evidence, not a stack high-water measurement or future headroom
claim. The primitive adds no allocation or unsafe site. All 208 ABI-15 and 151
ABI-6 clients rebuild byte-identically to their qualified baseline; no new legacy
target campaign is claimed. All ten development gates pass in run-aoks0khj.

The emitted full reclaim occurrence remains Reserved. Fixture disposal is not
execution/acknowledgment of that occurrence and does not apply Cleaned. Next is
exact issued-reclaim execution and acknowledgment, then Cleaned handling under
BG-057/BG-058. Provider Terminal, general mixed cuts, generated-source errno
variants, sustained retention (BG-060), recovery (BG-033), new-profile catalog
support and independent review remain open. No production POSIX, physical-target,
performance or release-readiness claim follows. There is no current kernel blocker.

intake/ retains the original small producer files, source/SDK archives, complete
packet byte-verification receipt and the explicitly local normalized producer.
The upstream 1.1 GiB target archive remains at its recorded producer location;
its digest was verified before extracting the selected original artifacts.
witness/ retains all 214 raw images, envelopes, serial/QEMU logs, commands,
source identities and client source. Generated ISOs stay in private out/ with
digests in reports. profile-boundaries/ retains the independent 32-case replay.
abi15-build/ and abi6-build/ retain compatibility images, commands and logs.
validation/ and rust/ retain the ten-gate and Rust witnesses. Scripts and logs
record exact local intake/build/replay steps. adoption/ captures current docs;
sha256.json seals this bundle. Packet byte identity is not signer authentication.
No failed consuming builds or target tests occurred in this step.

Final adoption refresh: all ten gates pass in `run-f_qq3yis` with unchanged checked
inputs. post-validation/, post-rust/ and postchecks.log retain that refresh.
