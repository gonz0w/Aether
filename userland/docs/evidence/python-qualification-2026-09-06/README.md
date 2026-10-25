# Python minimum-series qualification — UL-073

For maintainers checking quality-tool acceptance and the manual review handoff.
Built official CPython 3.10.21 and 3.12.14 sources in private build directories
using Clang 21.1.8 and GNU make 3.81. Nothing was installed into a real prefix.
The published SHA-256 values match both archives before extraction/build.
Source release pages and sources.lock.json retain the input identities; no GPG
or Sigstore signature verification, general source-trust certification or complete
reproducible bootstrap claim is made.

## Results and how to rerun

Each runtime passed 12 invocations: interpreter identity, the eight-method/ten-case
process suite, integrity controls, normal quality gate, expected release rejection,
help/version, two usage rejections and all three standalone standards wrappers.
The process suite exercises actual descendant cleanup and wrong-pin no-execution;
this is executed minimum-series evidence, not merely grammar validation.
Exact per-case expected/observed results and process receipts are in each version
directory. These results cover these patch releases, not every older patch or all
userland tooling. No native Aether execution is involved.

From the checkout root, the actual runtimes are:

```sh
build/python-qualification/Python-3.10.21/python.exe -B docs/quality/test-processes.py
build/python-qualification/Python-3.12.14/python.exe -B docs/quality/test-processes.py
```

Use either interpreter with `-B docs/quality/check.py` for the normal gate.
Verify sources.lock.json and each runtime-files.json before reusing retained
builds. Archives and runtime payloads remain local in build/; those manifests
are identities, not backups. Keep them until an explicit retention handoff.
The configured prefix directories are unused; these are source-tree runtimes.

## Provisioning limits and retained attempts

The initial sandbox downloads failed DNS. Authorized network downloads succeeded.
Release pages arrived gzip-encoded; a checksum text matcher initially missed their
nested HTML spans. Decoding the response and stripping checksum-cell markup matched
both explicit published pins. The build driver also checked its fixed digest before
extraction, independently of that page-text matcher.

Python 3.12's first make hit the inherited 16 MiB file-size limit on libpython3.12.a.
The failed attempt is retained; retry used a 128 MiB build-artifact limit and passed.
This changes no quality test's 16 MiB output bound. Four make jobs and a 600-second
build deadline were recorded. Compiler warnings are upstream build output, preserved
without rewriting upstream source or imposing first-party warning policy.

These are scoped offline test runtimes, not complete Python installations. Python
3.10 reported missing _gdbm/_hashlib/_ssl/ossaudiodev/spwd and an _lzma build failure.
Python 3.12 reported missing _gdbm/_hashlib/_lzma/_ssl/_tkinter. The exercised quality
paths work with available modules and built-in hash implementations; this does not
qualify TLS, compression modules or unrelated programs needing those facilities.
Dependencies, host SDK discovery, flags and exact build output remain in logs and
Makefile/pyconfig snapshots. No pip provisioning or global tool upgrade occurred.

## Manual review remains pending

The user volunteered to perform independent review manually. The actionable
[review packet](../../quality/MANUAL-REVIEW.md) identifies the code commit, technical
checks, separate reader walkthrough and fields to return. No reviewer decision or
signature has been invented. UL-072's missing Python-series execution is addressed
for the tested scope; independent review still blocks acceptance. UL-071's visual,
reader and packaged target lookup requirements remain separate.

Standards release pins, native interfaces and sibling repositories are unchanged.
The old records of missing runtimes remain immutable historical observations.

Staged whitespace validation initially rejected verbatim upstream/generated
Makefiles, configuration/source pages and build logs. Twelve exact-path attributes
now exclude only their preserved whitespace from that check; authored code/docs
remain checked. whitespace-review.json retains the initial output and decision.
No evidence bytes were reformatted and no hook was bypassed.
