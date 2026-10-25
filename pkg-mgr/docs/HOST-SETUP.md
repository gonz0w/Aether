# Experimental host setup

> Scope update, 2026-09-06: Aether is the only release target. This document
> preserves the earlier host-preview work; its macOS release/setup gates are
> superseded by [Aether release acceptance](AETHER-RELEASE.md). Host results remain
> development evidence and are not native package-manager acceptance.

The currently observed host is macOS 27.0 build 26A5421a, arm64, using Xcode-beta's
Apple clang 21.0.0 and macOS SDK 27.0. This is a development host observation, not a
promise that other macOS versions, Linux or BSD are qualified. No installer is run
by this project and no Apple SDK/tool binaries are bundled.

Before qualifying a host source snapshot, run:

```sh
python3 tests/check-host-setup.py
```

The check requires macOS arm64, Python 3.10+, GNU Make 3.81+, ShellCheck exactly
0.11.0, sh and the named Unix file/text utilities, a SHA-256 tool, a C compiler,
mandoc, man and tar. These are already-installed tools. Python and ShellCheck are
development requirements; mandoc/man are release-documentation requirements.
Minisign enables the live signature fixture; absence is recorded explicitly.
This preflight does not replace executing the fixtures or compiler/manual examples.

The printed private directory retains result.json, including tool paths, resolved
paths, hashes, probe stdout/stderr and exit statuses. Missing required tools or
failed probes leave a blocked result and a nonzero exit. This profile deliberately
rejects other host OS/architectures until their own qualification exists. It does
not change normal portable fixture checks or package-manager runtime behavior.

On Apple hosts, `/usr/bin/cc` and `/usr/bin/make` may be identical tool-selection
shims. Their hashes alone do not identify the selected compiler/build tool. The
preflight also records `xcode-select -p`, `xcrun --find cc`, `xcrun --find make`,
selected executable hashes, the SDK path/version and SDKSettings.json hash.
DEVELOPER_DIR, SDKROOT and CC overrides are recorded as observations. Any override
must be accounted for in the actual build receipt; this preflight invokes `cc`
and `make` from PATH and does not qualify an alternate CC on its own.

The recorded host used Python 3.14.7, GNU Make 3.81, ShellCheck 0.11.0 and bsdtar
3.5.3. These installed-tool observations do not supply a reproducible acquisition
recipe, pin the complete SDK/library/toolchain closure or approve a public release.
Exact reviewed installation inputs and an independent setup/build witness remain
HR-06 work. Do not substitute a moving package-manager install command for those
missing inputs. Tool upgrades invalidate affected setup/build evidence.

After setup, run the [source snapshot qualification](SOURCE-SNAPSHOT.md). The host
checks use local inputs after setup; network denial is a separate unproven boundary.


## Acquisition audit and the next builder

The [2026-09-06 local acquisition audit](evidence/host-acquisition-2026-09-06/README.md)
traced 15 package/version identities from the installed Python, ShellCheck and
minisign receipts. Thirteen exact installed receipts were available. OpenSSL 3.6.3
records ca-certificates 2026-05-14, and zstd 1.5.7_1 records xz 5.8.2; neither exact
receipt version remains in this Cellar. These edges need reconciliation with the
actual selected libraries before claiming dependency closure. Do not silently
substitute the newer installed versions into the old receipts.

One matching cached bottle was available: minisign 0.12 arm64_tahoe, SHA-256
3978ab782bb253378c31e91a018a64f5ebffd3f7094f7a731e47b09ed1424123. Its digest matches
the saved bottle manifest. This is a local metadata binding, without publisher
signature verification. Other recorded package versions lacked matching cache
archives in the inspected download directory. No formula was executed and no
package was installed, upgraded or removed.

The maintainer confirmed that the macOS 27.0 build 26A5421a and Xcode 27.0 build
27A5194q installers/VM image were not retained. Installed version metadata alone
cannot recreate that environment. The original candidate's recorded host tests
remain scoped to the observed machine; exact reconstruction is unavailable from
these retained inputs.

To close HR-06, qualify a newly captured builder rather than reconstructing missing
inputs by assumption:

1. Select the builder OS/toolchain and retain permitted installation media or a
   restorable builder image. Record exact supplier/version, digests, setup commands
   and applicable terms before installation. Keep proprietary media outside the
   public source package and use the supplier's authorized acquisition route.
2. Capture the complete selected tool/dependency inputs, with an acquisition digest
   for each artifact. Reconcile receipt edges with the libraries actually selected.
   Preserve original metadata; missing artifacts and unresolved edges stay blocked.
3. Restore/install into a clean builder and record setup commands/results and tool
   identities. Run the candidate's host preflight, full suite and required manual/
   bytecount checks, retaining failures and the candidate archive hash.
4. Obtain the independent setup/build witness. If its OS, compiler or SDK differs
   from the current profile, record a new profile and fresh evidence; do not transfer
   the earlier host result to it. Content, security contact and release approval
   remain separate gates.

This route is planned acceptance work, not an executed clean installation. It does
not add a host package installer, bootstrap framework or runtime dependency here.
