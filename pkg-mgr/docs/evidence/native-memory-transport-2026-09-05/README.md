# Native-memory package transport — 2026-09-05

The accepted userland memory consumer was extracted from its pinned positive ISO,
staged through the explicit memory transport, rebuilt into an image and booted.
Both generations report 24 initial pages used / 104 remaining, exit 0, and
supervisor cleanup reclaimed=2 before `AETHER NATIVE IO PASS`.

Retained root: `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-native-memory-2026-09-05`.
It contains all staged payloads, source ISO extraction, rebuilt ISO, command logs
and raw serial output. [result.json](result.json) pins producer results/source
inventory, transport receipt, rebuilt image, serial, harness and implementation.
[commands.json](commands.json) records exact executed commands.
[receipt.json](receipt.json) binds all six transported payloads.
[serial.log](serial.log) is the consuming native witness.

Reproduction command:

```sh
python3 tests/native-memory-integration.py \
 --producer /Users/cam/DEV/Aether-userland/build/native-memory-userland-final \
 --results-sha256 d9d4c91d2edb444817fad83d70b2797253fbf84ee5dc91033a90a495bc9dd7d1 \
 --sources-sha256 1a81beb2bfe066839410824e70d85b3241ba1d786cfe4e7d24882696a235c0b6 \
 --root /absolute/new-private-root
```

The [ordinary fixture log](fixtures.txt) covers legacy and memory-profile transport
checks plus the existing package suite. No sibling source, released standard or
consumer pin changed. No native pkg-mgr execution, live installation, release
approval, authenticity, power-loss durability or general POSIX support is claimed.
