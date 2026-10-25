# CLI validation — 2026-09-05

- `sh tests/check.sh`: three pinned standards checks and thirteen fixtures pass.
- `sh tests/zlib-integration.sh /tmp/pkg-mgr-zlib-1.3.2.tar.gz`: real source build,
  binary transport and retained replacement through the CLI pass. Output roots
  were disposable; paths in these logs are not retained artifacts.
- `sh tests/cli.sh` rerun after adding the explicit non-ASCII plain-output case:
  passes. The suite log predates that additional assertion only.
- Host PTY smoke check (Python `pty`, actual CLI against a nonexistent root):
  auto color emits ANSI with TERM=xterm and NO_COLOR empty; NO_COLOR=1 and
  TERM=dumb each suppress it. All three preserve failure exit 1 and empty stdout.

Host evidence only. The suite's deliberate SIGKILL diagnostics are expected.
No wrapper-wide cancellation, durability, Linux/BSD runtime or native Aether
execution claim is made. See [CLI contract](../../CLI.md).
