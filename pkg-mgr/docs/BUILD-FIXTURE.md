# Local package fixture contract

Implemented: 2026-09-05. Host tooling uses GNU Make 3.81+ syntax and POSIX sh. Tested here with GNU Make 3.81 on macOS. BSD make and Linux/BSD runtime execution have not been validated.

## Commands

From the repository root:

```sh
fixture_root=$(mktemp -d)
make -f mk/pkg.mk ROOT="$fixture_root" init-root
make -j8 -f mk/pkg.mk ROOT="$fixture_root" package
cat "$fixture_root/manifests/hello-local.manifest"
make -f mk/pkg.mk ROOT="$fixture_root" clean
```

ROOT must be an existing, empty, caller-owned mode-0700 directory at initialization. `init-root` creates `.pkg-mgr-root` containing `pkg-mgr-fixture-v1`. Subsequent operations require that marker. HOME, the working directory, common system directories, symlink roots, and dot/parent components are rejected. ROOT has no trailing slash, tab, or newline; spaces and apostrophes work. Parent paths may resolve through host aliases such as macOS `/tmp`.

The fixture layout is fixed:

```text
ROOT/
  .pkg-mgr-root
  distfiles/hello-local.txt
  work/hello-local/{hello.txt,config.mk,build/hello.txt}
  stage/hello-local/usr/local/share/hello-local/hello.txt
  manifests/hello-local.manifest
  logs/hello-local/phase.log
```

PREFIX selects an absolute path *inside* the stage; it must have nonempty components with no `.` or `..`, trailing slash, tab, or newline. The default is `/usr/local`. DESTDIR and other output overrides must match the derived ROOT layout. Each recipe selects one validated `DISTNAME` basename below ROOT/distfiles. The hello-local fixture retains the shown layout; [zlib and zpipe](ZLIB-PACKAGE.md) now exercise real source phases through the same driver.

Every phase helper checks the root before mutation. Existing symlinks, hard-linked files, special files, and extended root ACLs reported by `ls` are rejected. There is no automatic fallback to checkout paths or a real installation prefix. `clean` refuses packages registered in the [state fixture](PACKAGE-STATE.md); for unregistered packages it removes only this package's copied source, work, stage, log, and path manifest; it retains the root marker and unrelated files. Invoke `clean` and `init-root` separately: combining either with another target fails before recipes execute.

## Ordering and integrity

Make prerequisites form a chain from fetch through manifest. Requesting a later phase runs its prerequisites; requesting several phases in one parallel make executes each only once. Phases are phony, so a later invocation rebuilds prerequisites rather than reusing unchecked stamps. Logs append until clean.

Fetch copies LOCAL_SOURCE to DISTFILE. Verify passes **DISTFILE** to the existing strict source-record verifier and compares SHA-256 and size against SOURCE_METADATA. A malformed record, failed hash tool, missing input, size mismatch, or digest mismatch blocks extraction. SOURCE_TARGET controls only the standalone metadata command; it cannot redirect verification in `package`.

The manifest helper generates validated, sorted hash rows, projects their paths, and replaces the path manifest only after both operations succeed. A failed manifest projection preserves the prior manifest. Tested verify/build failures leave prior staged payload and manifest unchanged, though scratch files and logs may change. This is not a transaction covering every build/stage write.

## Trust and limits

Recipes, make variable expressions, tool overrides, input metadata selection, and the caller's environment are trusted. Checking bytes against caller-selected metadata is integrity evidence, not source authenticity. A hostile recipe can execute arbitrary host commands; no sandbox is implemented.

Use one make process per private root. Ordering within a parallel invocation is tested; separate concurrent writers, hostile filesystem races, bind mounts, power-loss durability, and full ACL policy are not covered by these shell checks. A root marker is an accidental-use guard, not an authentication token.

Standalone metadata targets (`hashed-manifest`, `build-record`, and verification helpers) keep their existing explicit input/output interfaces. They do not acquire the package workflow's ROOT confinement contract and must receive caller-controlled paths. No binary eligibility or final-install decision follows merely from their exit status.

## Validation

`sh tests/check.sh` runs ten active scripts, including package-state validation. `tests/package-boundary.sh` compares serial/parallel logs and payloads, corrupts only the fetched copy, injects manifest-tool failure, checks preservation of prior outputs, and rejects unsafe root/override/link/special-file cases. The older happy-path and failure checks now use their own private roots rather than cleaning checkout output directories.
