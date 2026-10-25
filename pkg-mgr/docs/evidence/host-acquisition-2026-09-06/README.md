# Host acquisition audit — 2026-09-06

This read-only local audit records why the qualified host cannot currently be
reconstructed from retained installation inputs. It does not invalidate the
[candidate qualification](../candidate-refresh-2026-09-06/README.md) on that host.
HR-06 remains open under the [setup acceptance plan](../../HOST-SETUP.md).

## Method and observations

`python3 docs/evidence/host-acquisition-2026-09-06/capture.py` resolved the installed
Python, ShellCheck and minisign executables, traversed exact runtime dependency
identities in Homebrew INSTALL_RECEIPT.json files, and copied available receipts
and formulas unchanged. The capture script is a one-off evidence artifact, not a
supported setup command. Do not rerun it over this historical evidence directory.
No formula was executed and no installation, upgrade or network fetch occurred.
Original third-party metadata and terms remain unchanged.

[acquisition.json](acquisition.json) records 15 package/version identities, 13
available receipts and two missing exact receipts:

- openssl@3/3.6.3 references ca-certificates/2026-05-14.
- zstd/1.5.7_1 references xz/5.8.2.

These historical receipt edges are not proof of broken installed tools or complete
runtime linker closure. A future builder must reconcile its actual selected
libraries rather than silently substitute versions into historical receipts.
Each available receipt/formula has its source identity and SHA-256 recorded.

Exact name/version cache discovery found one matching archive among the inspected
Homebrew download entries: minisign 0.12 arm64_tahoe. Its SHA-256 is
3978ab782bb253378c31e91a018a64f5ebffd3f7094f7a731e47b09ed1424123.
[cached-bottle-check.json](cached-bottle-check.json) records its digest match against
[minisign-bottle-manifest.json](minisign-bottle-manifest.json). This is local
metadata comparison, not publisher authentication. No other matching archives
were found for the recorded versions in that inspected directory; this is not a
claim about supplier availability or every possible location on the host.
[retained-cache.json](retained-cache.json) identifies the unchanged bottle copy in
an ignored private directory. The bottle was neither extracted nor installed.

[Xcode-version.plist](Xcode-version.plist) preserves installed Xcode 27.0 build
27A5194q metadata. In this task the maintainer answered “I dont” when asked whether
macOS 27.0 build 26A5421a and Xcode 27.0 build 27A5194q installers or a VM image
were retained. Installed metadata cannot replace those missing installation inputs.
The setup gate therefore requires a newly captured builder and fresh qualification,
including an independent setup/build witness. No clean installation was attempted.

## Validation and limits

This change updates documentation and retains observations; it changes no runtime
command, format, pinned standard or public candidate archive. The development
inventory already covers HOST-SETUP; the evidence capture is not a new product
subsystem. Selected checks are whole-shell development validation, the offline
standards gate and whitespace validation. Logs retain their exit statuses; the
runtime suite was not repeated for this documentation-only change.

SHA256SUMS binds this evidence recursively. validation-inputs.json records exact
dirty-tree document/checker inputs before validation. These hashes establish local
identity, not independent review or provenance authentication. Existing test results
remain scoped to the previously qualified archive and observed host.

All three selected checks passed (exit 0). Capture-script syntax, copied receipt/
formula hashes and the retained bottle digest also verified successfully.
