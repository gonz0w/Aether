# Private native entropy qualification — 2026-10-04

[Before-code contract](contract.md) / [reference](../../NATIVE-ENTROPY.md).
This is real QEMU hardware transport with explicit per-domain authority, not public
SDK adoption, entropy quality, physical hardware or general service qualification.

Attempt1 fails before compilation: helper imports lack the scripts search path.
Attempt2 fails build: native_threads was referenced before declaration. Original
recipes and the failed build source are retained. Attempt3 passes3 native cases.
Fresh final attempt4 passes all4, adding supervised real generation1→2 replacement.
Both domains draw at an exact protected-page boundary; reject foreign/old-generation,
zero/oversized/reserved, read-only/unmapped/cross-page/overflow destinations without
changing inspected bytes or quota; exhaust4096 bytes, close permanently and reject
repeated close. Disabled route is-38. Omitted kernel quota consumption fails both
at terminal253 with the exact panic oracle. Existing TLS/memory/output/64-yield
checks are unchanged. Rust supervisor completes3 reclaims and generation-bound
fresh quota; old selectors are denied after replacement.

Full host checks pass137 Python cases plus Zig/Rust/offline pins/workflow, including
portable grant/close/quota tests. All11 hardware entropy and7 M4 regressions pass.
Five older native block cases pass. First block setup expects evidence.json absent
from guarded delivery; retry copies build-evidence.json under the private legacy
filename with identical bytes, preserving the staged/sealed SDK. That failed
attempt and explicit adaptation receipt are retained. No mutable sibling bytes,
released standards pins or public SDK are changed.

Guards validate every output byte before DMA. One BSP owns device state under IF
clear; user teardown/unmap cannot overlap copied synchronous completion. DMA stays
reserved on hardware failure; output/stack copies are cleared after successful
transfer. The fixture quota is not an engine memory/entropy admission decision.
No statistical tests, independent side-channel review, IOMMU/physical hardware,
service latency/restart policy or production entropy certification is claimed.

Reproduction is documented in NATIVE-ENTROPY. The SDK intake verifies all1979
members of the retained provider packet and selects241 regular SDK files. Compile
with exact Clang/LLD21.1.8, Rust1.98.0 and Zig0.16.0 flags; QEMU11.1.1/qemu64 on
q35/TCG, pinned firmware. Each build180seconds, VM30seconds and owned teardown3
seconds; forced kill fails. Logs, actual QEMU commands, tools/artifacts/source
identities and UTC times remain in the archive. All archive members read back
before only owned verified duplicates are removed. Earlier AES and hardware
entropy evidence stays sealed. New original code is BSD-2-Clause; musl payloads
retain their upstream notices and existing guarded producer licensing.

Next actual libzpool random helper port using this checked explicit grant; public
SDK facade/consumer adoption belongs to userland. Whole-engine initialization,
provider/configuration/feature/resource/thread closure and persistent filesystem
composition are still open.
