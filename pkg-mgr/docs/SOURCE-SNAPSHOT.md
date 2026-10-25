# Development source snapshot

This is an HR-06 preparation tool, not the public release packager. Run from the
checkout with Python 3.10+ and host tar already installed:

```sh
python3 tests/check-source-snapshot.py
```

The printed private root retains source.tar, repeat.tar, input-files.json,
result.json and extracted/pkg-mgr. Sorted regular files from bin, mk, recipes,
fixtures, manifests, tests, man, docs and .githooks are included, plus the root README,
AGENTS, CONTRIBUTING, SECURITY, LICENSE, .gitignore and three active planning documents.
The embedded SOURCE-MANIFEST.json binds exact paths, ordinary modes, sizes and
SHA-256 digests. PAX format preserves long historical paths. Fixed tar owner/time metadata makes repeat assembly comparable.
Generated work/stage/log/distfile roots, version-control state, retained live roots,
Python caches and Finder metadata are excluded. Hook files are included as source;
assembly/extraction does not install hooks or create Git metadata. Missing inputs, links, hardlinks,
special files/modes, changed inputs and extraction differences fail the check.
The source tree must remain under caller control without concurrent writers.

The archive is extracted using the installed host tar and compared to the captured
input manifest. Never use this tool to extract an arbitrary downloaded archive.
Python remains a development-only dependency; the package-manager runtime is still
shell/make. This local tool uses only the Python standard library and host tar;
update/remove it with the development tooling, without changing package protocols.

For source-closure qualification, change directory to the extracted/pkg-mgr root
and run:

```sh
sh tests/check.sh
python3 tests/check-manuals.py --render-required --binary-example
```

These require the documented developer tools: Python 3.10+, ShellCheck 0.11.0,
GNU Make 3.81+, sh, Unix text/file tools and SHA-256 support; the second command
also requires mandoc, man and a host C compiler. Record actual versions and hashes
for each qualification run. No tool installation or network download is performed
by the snapshot command. A relocated host witness is not a network-confinement test
or an independent reviewer witness.

This development snapshot deliberately retains documentation history/evidence to
preserve current references. It also includes optional native and zlib/zpipe source
recipes as development material. Their presence does not qualify those workflows
for the preview; zlib's external source archive is not bundled. Historical logs,
third-party material and draft references need publication review/pruning before
selecting a public source inventory. No signature, tag, upload, security-support
promise or release approval is created. See [the release gates](HOST-RELEASE.md).

Run the [installed-host preflight](HOST-SETUP.md) before collecting a new witness.
The [public content review](RELEASE-CONTENTS.md) excludes history from the proposed
public package; this development snapshot continues to retain it deliberately.
