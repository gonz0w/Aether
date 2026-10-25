# Four-channel process/file coexistence witness

2026-09-05. [Contract and reproduction](../../NATIVE-COEXIST.md).
Six new cases pass: routed seed/scratch access across two backend generations,
repeated collection, partial request, requester exit, insufficient channel pool,
and corrupted file-read data. Exact requester/broker rejection codes and reclaim
counts distinguish the negative controls from unrelated failures.

Regressions pass: six process, five launch, seven lookup, four channel, three
read-only files, five writable files, seven init, eleven native-memory and twelve
frozen userland/sys-init legacy consumer cases. Default two-core smoke and
framebuffer verification pass. Host tests, 44 Python tests, three offline standards
checks, Rust/Zig formatting, Python compilation and help/mode rejection pass.

`summary.json` pins the source archive, individual source files, suite reports and
host/tool versions. Captured suite source hashes were verified against the final
working files before retention. The archive includes kernel, fixtures, scripts,
boot/toolchain pins, host tests, domain contracts and offline standards. Explicit
strict-musl and compiler/linker dependencies remain separate pinned inputs.
Small ELF/envelope/raw files, maps, reports and logs are retained; large ISO/kernel
outputs stay at the private paths in the reports. No automatic sibling lookup or
network fetch is introduced by the build.

This is Aether producer evidence. The legacy companion regression remains its
older profile; it does not count as userland adoption of ABI 7. No companion
sources or immutable standard/consumer pins changed. Old profile capacities and
markers are preserved by the separate new profile. The broker stays within its
4 KiB immutable page at 3944 bytes using size optimization and fat LTO; early
oversized link attempts were not executable acceptance.

Transport coexistence does not implement shared descriptor inheritance, fork,
in-place exec, program-plus-file-service process capacity, recovery after arbitrary
transport loss, native dash or persistent package installation. Those remain
explicit next integration requirements, not implied by this successful fixture.
