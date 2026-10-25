# First real source packages: zlib and zpipe

Implemented and tested: 2026-09-05. `zlib` 1.3.2 builds as a static library, runs upstream tests, stages its headers/library/documentation/license, and registers a package record. `zpipe` 0.2 is a small local C stream filter that compiles against the registered staged zlib headers and exact `libz.a` path. These are host packages, not Aether-native binaries.

## Source pin and build boundary

The source archive is [zlib's official 1.3.2 tar.gz](https://zlib.net/zlib-1.3.2.tar.gz). Its [upstream release page](https://zlib.net/) publishes SHA-256 `bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16`. The downloaded archive matched that digest and measured 1,502,830 bytes. `recipes/zlib/source.kv` pins both. This establishes a match to the observed publisher digest, not independently verified signer governance or complete source authenticity.

Fetching is separate from building. No download step is hidden in the recipe, and the ordinary suite requires neither a network nor zlib's archive/compiler. The opt-in integration test consumes a local pinned archive. Upstream build scripts and the host toolchain remain trusted; no network or filesystem sandbox is enforced around them.

The existing GNU Make phase chain now delegates the six explicit recipe phases to a small shell script selected by `package.mk`. The hello-local actions moved to `mk/hello-phases.sh`; phase ordering, logging, verification, and root guards stay shared. `DISTNAME` is a validated single basename under the fixed distfiles directory. This adds no recipe language or plugin registry.

## Reproduce the two-package workflow

From the repository root, fetch once if the archive is not already available:

```sh
archive=/tmp/pkg-mgr-zlib-1.3.2.tar.gz
curl --fail --location --proto '=https' --tlsv1.2 \
    --output "$archive" https://zlib.net/zlib-1.3.2.tar.gz
```

Build and register using only the local archive:

```sh
fixture_root=$(mktemp -d "$PWD/.pkg-mgr-live-zlib.XXXXXX")
make -f mk/pkg.mk ROOT="$fixture_root" PKGNAME=zlib init-root
make -j4 -f mk/pkg.mk ROOT="$fixture_root" PKGNAME=zlib \
    SOURCE_ARCHIVE="$archive" register
make -j4 -f mk/pkg.mk ROOT="$fixture_root" PKGNAME=zpipe register
printf 'zpipe\n' > "$fixture_root/state/world"
sh mk/state.sh list "$fixture_root"
sh mk/state.sh verify "$fixture_root"
sh mk/state.sh orphans "$fixture_root"
"$fixture_root/stage/zpipe/usr/local/bin/zpipe" --version
```

Expected package list:

```text
zlib    1.3.2    dependency
zpipe   0.2      explicit
```

The output is tab-separated. The orphan report contains its non-deleting header and no candidates. Registration does not edit `world`; the explicit command above selects the utility and keeps its dependency reachable.

`package` runs through staging/path manifest; `evidence` additionally generates a hash manifest and advisory source/build/SPDX records; `register` additionally registers the result, initializing state if absent. Evidence currently requires ROOT beneath the checkout because the existing build-record helper resolves repository-relative material references. The zlib recipe also requires ROOT/PREFIX paths without whitespace or shell metacharacters because upstream make uses unquoted paths. The original hello fixture still supports spaces and apostrophes.

Host prerequisites are a C compiler named by `CC` (default `cc`), make, tar/gzip support, standard shell/text tools, and a SHA-256 implementation. CC must name one executable, not a shell command with flags. The live run used Apple clang 21.0.0 targeting `arm64-apple-darwin27.0.0`. No cross-compilation or Linux/BSD runtime result is asserted.

## What the recipes prove

The zlib phases verify the copied archive before extraction, reject unexpected top-level paths and non-file/directory archive types, run `./configure --static --prefix=...`, build, run `make test`, and use upstream `DESTDIR` installation into the private stage. This is a pinned-release extractor, not a general untrusted-archive service. Static mode avoids shared-library symlinks that the state model cannot represent yet.

The zpipe recipe requires a registered zlib package and verifies current staged state before compiling. It uses `-I` pointing at staged headers and the full staged archive path; it never uses `-lz` or pkg-config to discover a host substitute. A damaged dependency prevents compilation. macOS `otool -L` confirmed no dynamic zlib dependency; the executable still depends on the host system runtime, so it is not a fully static executable.

`zpipe c` encodes a zlib-format stream from stdin to stdout; `zpipe d` decodes one stream. This is not a gzip/ZIP utility. It rejects truncated, malformed, and trailing data and checks I/O results. A failed decode may already have written a prefix of output; it does not promise transactional output. Tests cover empty, text, multi-buffer binary data, and the full source archive.

Both recipes stage a package-owned `share/pkg-mgr/NAME/host.kv` observation. The manifest therefore binds host OS/architecture, compiler target/version, recipe/phase/driver hashes, and—for zpipe—the exact zlib record hash used. The separate build source record points to the verified local copy, while the checked-in source pin retains the upstream URL. This is an advisory observation, not a full dependency/SBOM attestation, environment lock, or reproducible-build proof.

## Validation and saved artifacts

```sh
sh tests/check.sh
sh tests/zlib-integration.sh /tmp/pkg-mgr-zlib-1.3.2.tar.gz
```

The ordinary suite has eleven scripts and remains local/no-compiler. The opt-in test builds both packages, runs upstream and utility tests, checks dependency/ownership/world behavior, refuses a same-size changed source and corrupted dependency, and checks static linkage when `otool` is available. Both passed on this macOS host.

Historical 0.1 evidence: [saved run identity](evidence/zlib-2026-09-05/run.kv) names the retained private root (ignored by Git). [Upstream build/test log](evidence/zlib-2026-09-05/zlib.log), [utility log](evidence/zlib-2026-09-05/zpipe.log), [package list](evidence/zlib-2026-09-05/packages.tsv), [ownership](evidence/zlib-2026-09-05/owners.tsv), and [linkage](evidence/zlib-2026-09-05/linked-libraries.txt) are retained with both package records/manifests and host observations. The library, headers, and runnable utility remain in that root for inspection. Registered payloads cannot be rebuilt or cleaned through make; use a fresh root for another experiment.

Directory binary transport, ordinary permission preservation and retained private-root replacement are now implemented. Live-prefix installation, payload deletion, Aether ABI support, sys-init activation and production trust policy remain separate work.

## Real replacement from 0.1 to 0.2

Version 0.2 adds `--help`, which prints usage to stdout and exits zero. The frozen 0.1 source and its hash/size pin live under `fixtures/sources/zpipe-0.1/`; its `--help` remains an unsupported argument with exit 64. Compression/decompression behavior is unchanged.

The opt-in integration test builds 0.1 using explicit `PKGVERSION`, `LOCAL_SOURCE` and `SOURCE_METADATA` overrides with the current shared recipe phases. This is a build of the preserved old source through today's tooling, not a claim to reproduce the historical executable bit for bit. It builds 0.2 in a separate root against the exact same imported zlib record, exports it, preflights/prepares/finishes replacement, and verifies both versions. No rebuilding occurs inside the installation destination.

```sh
# Default cleans its disposable roots after the test:
sh tests/zlib-integration.sh /tmp/pkg-mgr-zlib-1.3.2.tar.gz
# Retain the generated private roots and executables for inspection:
KEEP_ROOT=yes sh tests/zlib-integration.sh /tmp/pkg-mgr-zlib-1.3.2.tar.gz
```

The retained path is printed at exit and is ignored by Git. Tests verify the active utility reports 0.2 and accepts help, the retained old executable reports 0.1 and still rejects help, both pass malformed-input and round-trip checks, and streams produced by either version decode with the other. World, the zlib record, and the proposed zpipe record are compared byte for byte. Recorded results are in [real replacement evidence](evidence/real-replacement-2026-09-05/run.kv).
