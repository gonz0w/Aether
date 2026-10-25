# pkg-mgr experimental host preview candidate

> Scope update, 2026-09-06: Aether is the only release target. This edition
> preserves the host development baseline; it is not a native Aether release.
> Earlier macOS preview/setup release gates below are superseded by
> [Aether release acceptance](docs/AETHER-RELEASE.md).

This source package is a local release candidate under review. It has not been
approved for publication or supported security service. The initial qualification
profile is macOS arm64 with GNU Make; other hosts require separate evidence.

Start with [host prerequisites](docs/HOST-SETUP.md), [CLI usage](docs/CLI.md),
[package records](docs/PACKAGE-STATE.md) and [binary transport](docs/BINARY-PACKAGE.md).
Offline references are [pkg-mgr(1)](man/pkg-mgr.1), [pkg-state(5)](man/pkg-state.5)
and [pkg-binary(5)](man/pkg-binary.5). Run from this extracted directory:

```sh
python3 tests/check-host-setup.py
sh tests/check.sh
python3 tests/check-manuals.py --render-required --binary-example
```

The normal suite uses initialized private roots. The compiler example builds the
bundled bytecount source, registers it, exports/imports it and checks execution.
For a compiler-free example, use the [CLI tutorial](docs/CLI.md). No sibling checkout
or source download is needed for those commands after host setup.

The scope is private-root build, stage, register, inspect, verify, local binary
transport and retained replacement/recovery. Live-prefix installation, remove/prune,
concurrent writers, remote repository authentication, durable crash recovery and
service activation are unimplemented or unproven. Native adapters and optional
zlib/zpipe recipes remain development material; the zlib archive is not bundled.

Historical logs, plans, research and agent instructions are omitted. Operational
references retain their original experimental context; omitted development links
are visibly marked. Their old progress statements are not acceptance evidence for
this archive. The pinned offline standards remain byte-identical.

[Content/notice scope](docs/RELEASE-CONTENTS.md), [contributor process](CONTRIBUTING.md)
and [release gates](docs/HOST-RELEASE.md) describe remaining work. A monitored security
contact, independent reviews and an explicit publication decision are still required.
Original work uses the included [BSD-2-Clause license](LICENSE); bytecount retains
its own matching notice. Upstream payloads and installed host tools retain their terms.
