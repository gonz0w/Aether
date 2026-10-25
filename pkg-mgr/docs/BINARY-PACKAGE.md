# Local binary transport

Implemented 2026-09-05 by `mk/binary.sh`. This experiment exports a registered host package and imports its regular files and exact record into another initialized private root. The imported zpipe executable runs without rebuilding; zlib must be imported first.

Format reference: [pkg-binary(5)](../man/pkg-binary.5). This document retains workflow and validation context.

## Commands

From the repository root, use the source root produced by [the zlib workflow](ZLIB-PACKAGE.md):

```sh
sh mk/binary.sh export "$source_root" zlib
sh mk/binary.sh export "$source_root" zpipe

fresh=$(mktemp -d)
make -f mk/pkg.mk ROOT="$fresh" init-root
sh mk/state.sh init "$fresh"

# Select the compiler target expected by your host policy. Recorded macOS demo:
expected_target=arm64-apple-darwin27.0.0
for name in zlib zpipe; do
    bundle=$source_root/binaries/$name
    pin=$(sh mk/verify-metadata.sh hash-file "$bundle/artifact.kv")
    sh mk/binary.sh import "$fresh" "$bundle" "$pin" "$expected_target"
done
printf 'zpipe\n' > "$fresh/state/world"
sh mk/state.sh verify "$fresh"
sh tests/zpipe-roundtrip.sh "$fresh/stage/zpipe/usr/local/bin/zpipe"
```

The locally calculated pin above demonstrates transport integrity for your own build. A digest delivered alongside an untrusted download does not authenticate it. Import requires an absolute bundle path, a caller-supplied descriptor SHA-256, and an explicit expected compiler target. It also matches the running host OS and architecture. These identity checks do not prove ABI compatibility, minimum OS version, CPU requirements, or native Aether support.

Export refuses an occupied `binaries/NAME`; import refuses an existing package or occupied stage. Neither command edits `world`. Dependencies are imported explicitly in order, with exact record fingerprints; there is no resolver or version substitution.

## Directory format

Each bundle contains exactly these top-level entries:

| Entry | Meaning |
| --- | --- |
| `artifact.kv` | Format `local-binary-directory-v2`; SHA-256 of the four tables below; explicit `authenticity=not-proven` and `service_activation=unsupported` |
| `package.tsv` | Exact [package-state record](PACKAGE-STATE.md), including canonical build evidence, dependencies, and file hashes/sizes/paths |
| `target.kv` | Format `host-binary-target-v1`, host OS/architecture, compiler target, `modes=recorded-0000-0777` |
| `modes.tsv` | Four-digit ordinary mode (`0000`–`0777`), TAB, logical path; one row per file in manifest order |
| `dependencies.tsv` | Dependency name, TAB, exact registered record SHA-256, in dependency order |
| `files/` | Regular-file blobs named by their SHA-256; repeated content shares a blob within this bundle |

This is a directory transport, not a tar reader or selected production store. It adds no archive dependency. The current recipes must contain a manifest-bound host observation at `usr/local/share/pkg-mgr/NAME/host.kv`; other prefixes/runtimes need a deliberate extension. Import compares target and dependency tables with this bound observation.

Export preserves the exact ordinary permissions recorded in pkg-state-v2, including private 0600 files. The mode table must equal the modes in that record. Set-ID/sticky bits are rejected. Owner/group, timestamps, ACLs, xattrs, directory modes, empty directories, symlinks, hardlinks, and special files are not preserved. Unsupported entry types are rejected. Normal state verification now checks permissions after import as well as content/size/path.

## Publication and limits

Existing state and payload are verified first. Import validates the descriptor, strict record schema, target, modes, dependency fingerprints, and blob content, then constructs a private candidate. Existing state registration validates candidate sizes, evidence bindings, dependencies and ownership conflicts before publishing its stage and record.

The root and bundle must remain under caller control with one writer throughout the operation. This is not hardened against hostile filesystem races. Ordinary failure between the two publication renames removes only this invocation's newly published, unregistered stage. A crash can leave an occupied, unregistered stage; later import refuses to overwrite it. [Explicit recovery](IMPORT-RECOVERY.md) can validate the existing stage against the pinned bundle and publish its missing record. There is no crash-atomic transaction, automatic recovery, update/remove operation, or authority to delete an existing package. Recipes and imported executable content remain trusted by the caller; hashes are not a sandbox or remote trust policy.

## Evidence

`sh tests/check.sh` includes compiler-free transport fixtures covering round trips, required dependencies, target and digest rejection, malformed paths/modes, altered blobs, unknown entries, links, duplicates, and injected record-publication failure. The opt-in `sh tests/zlib-integration.sh /absolute/zlib-1.3.2.tar.gz` now builds, exports, imports and runs the actual utility. A retained run is recorded in [binary evidence](evidence/binary-2026-09-05/run.kv).

Aether-userland owns the proposed base-package selection. At final review on September 5 it contained a compile-only C object probe, explicitly without libc, OS calls, entry point or target-runtime claims. No approved base list or package ABI was available. These zlib/zpipe demonstrations do not designate either package as part of Aether's base install.

The earlier v1 bundles and September 5 saved binary evidence describe the prior normalized-mode experiment. V2 transport rejects those bundles; rebuild into a fresh root to produce permission-tracked records and bundles. No automatic evidence migration is performed.


Descriptor generation checks all four table hash commands before emitting metadata.
Export also calculates the descriptor's receipt digest before publishing the bundle.
A failed required hash emits no export receipt and leaves the destination unpublished;
existing state and payload remain unchanged. Nine injected hash-helper failures cover
all five export digests and the four table digests during import revalidation.
Successful descriptor/receipt bytes remain unchanged. These checks establish ordinary
helper-failure handling, not remote authenticity or filesystem-race resistance.


Host identity, runtime, dependency observations and record-version reads must
succeed before their output is compared or used to construct a target record.
Plausible output accompanied by reader failure is rejected. Thirteen controls
cover five metadata fields during export/import and the host OS/architecture and
record-version readers during import, preserving target files/modes without
publication or success receipts. Ordinary compatible/incompatible identity behavior
is unchanged. A matching host identity remains an observation, not ABI proof.
