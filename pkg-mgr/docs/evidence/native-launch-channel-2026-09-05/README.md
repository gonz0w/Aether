# Native launch/channel/file transport evidence — 2026-09-05

Host: arm64 macOS; target: Aether x86-64 under QEMU. These are host-staged,
rebuilt-image consumer witnesses, not native package installation or signer trust.

| Study | Cases | Retained private root |
| --- | ---: | --- |
| Kernel launch | 5 | `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-launch-final-2026-09-05` |
| Kernel channel | 4 | `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-channel-final-2026-09-05` |
| Userland UL-038 channel | 6 | `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-userland-channel-2026-09-05` |
| Userland UL-039 read-only files | 4 | `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-userland-files-2026-09-05` |
| Kernel read-only files | 3 | `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-files-2026-09-05` |

Each study retains result, command, producer/tool inventories, receipts and serial
logs here. Large images and exact copied tools remain in the private roots.
`result.json` records exact implementation hashes and external producer/tool pins.
The producer JSON copies are normalized for readability; the external pin applies
to the original sibling evidence file, not the normalized copy.

The first four studies used `sources/native-launch-integration.py`; transport and
fixture sources are copied alongside it. Later consumer support is recorded with
its own harness snapshot so earlier results do not claim newer source bytes.
`macos-fixtures.log` records all three pinned standards checks and sixteen fixtures.

Reproduce with the [contract](../../NATIVE-LAUNCH-TRANSPORT.md), the appropriate
source snapshot, the original externally pinned evidence and a fresh private root.
Commands include absolute retained tool/artifact locations. No recorded command is
an instruction to execute without checking its inputs and scope.

Linux portability attempt: `linux/check.log` records three passing standards
checks and the first parser fixture, then exit 127 because this cached image lacks
`make`. No complete Linux package-suite pass is claimed. The frozen source inventory
and exact offline container command are retained in `linux/`. This environment gap
is separate from the native filesystem/process dependencies.

All 22 case outcomes pass: 20 boot checks and two structural rejections before
publication. UL-039 uses `userland-files/native-launch-integration.py`; it extends
the supported consumer schema/cases and retains distinct expected rejection details.
