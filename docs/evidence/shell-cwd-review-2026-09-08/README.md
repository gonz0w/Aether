# Scoped directory/CWD review

Documentation-only contract review. The
[local specification](../../NATIVE-SHELL-STARTUP.md#scoped-directorycwd-contract-review--2026-09-08)
selects a directory query grant, AECAT003 bootstrap, bounded owner operations and
facade behavior for unchanged generated dash init. No runtime implementation,
production filesystem assignment, full stat/POSIX claim or consumer acceptance.

Inspected generated init validates inherited PWD by stat device/inode comparison;
its fallback calls getcwd through cd.c. Inputs also retain userland's metadata
review and its separate Linux-target main/interactive-ENV configuration finding.
Sibling records are inspected inputs, not fresh consumer execution or sign-off.
Upstream source excerpts retain their original terms and COPYING in the archive.

Host command from repository root passed, including 98 Python tests:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

host.log retains output. inputs.json identifies exact review bytes; inputs.tar.gz
members were read back and verified. checks.json records simplicity snapshot,
links and prior runtime-source identity checks. manifest.json seals this packet.
No failed qualified check or QEMU run for this documentation-only step. Released
pins and sibling files are unchanged. Next: implement the bounded directory
owner/adapter and qualify the specified positive, rejection and cleanup controls.
