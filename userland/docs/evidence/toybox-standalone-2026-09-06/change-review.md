# UL-067 standalone cat/wc comparison plan

Before code: extend the existing offline reference builder with explicit cat/wc
single-applet configs (multiplexer off), preserving the existing default config.
This is equivalent explicit config selection, not invoking upstream single.sh in
retained trees. Keep shared Toybox settings comparable. Use fresh extraction roots,
pinned archive/Clang/musl/host helpers and record actual generated config/ELF/imports.
Migrate revised builder subprocesses to owned group cleanup/file bounds; generated
compiler launchers exec the selected compiler with inherited explicit build cwd/env.
No upstream patch, real-prefix install, dependency fetch or native port.

Build both; compare each ELF's size, symbols and config to immutable baseline.
Execute independent binary/empty/stdin/missing-file/full-output checks plus exact
upstream cat/wc suites under the existing pinned QEMU Linux image. Require nonzero
discovery, no skips and a deliberately wrong-output rejection. Each container has
no network/capabilities, read-only root/input, UID65534,512MiB/32PID and16MiB scratch;
45s independent/180s suite bounds, explicit named cleanup. No VM start/image pull.
Keep old build/evidence immutable and verify baseline hash. Source/ELF size findings
are not speed, native memory fit or security claims. Run quality/CLI/grammar checks
and retain all attempts. Original tooling BSD-2-Clause; Toybox/musl notices unchanged.
Shared O/I/E and CE/CP/TD/TE apply; independent review, source trust and native
startup/locale/umask/cleanup/output authority remain open. UL-059 waiting, UL-069 deferred.
