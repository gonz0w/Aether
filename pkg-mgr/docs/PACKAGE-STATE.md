# Private package-state contract

The [pkg-state(5) manual](../man/pkg-state.5) provides the offline format reference.
This page supplies helper commands, registration details and validation context.

Implemented: 2026-09-05. This is a regular-file staging experiment using POSIX sh, awk, and existing metadata helpers. It records observed packages without installing, activating, updating, or removing payloads.

## Commands and authority

```text
sh mk/state.sh init ROOT
sh mk/state.sh register ROOT MANIFEST BUILD-RECORD DEPENDENCIES
sh mk/state.sh check-register ROOT MANIFEST BUILD-RECORD DEPENDENCIES
sh mk/state.sh list ROOT
sh mk/state.sh owners ROOT
sh mk/state.sh files ROOT PACKAGE
sh mk/state.sh deps ROOT PACKAGE
sh mk/state.sh rdeps ROOT PACKAGE
sh mk/state.sh verify ROOT
sh mk/state.sh orphans ROOT
```

ROOT must already satisfy the [build fixture's private-root contract](BUILD-FIXTURE.md). State initialization publishes an empty `state/` directory containing `world` and `packages/`. Registration inputs are explicit absolute paths to readable regular files. The package name/version come from the supplied build record; its payload is always `ROOT/stage/NAME`.

`ROOT/state/packages/NAME.tsv` is authoritative. `ROOT/state/world` is the editable set of requested packages. No database, index cache, lockfile, or persistent generated report exists. All views are rebuilt from validated records, and invalid state produces no partial inspection/orphan output. Registration leaves `world` unchanged; register dependencies first, then edit `world` after the desired packages exist.

Package IDs and versions use `[A-Za-z0-9][A-Za-z0-9._+-]*`. Logical paths are relative, with ASCII letters, digits, spaces, `.`, `_`, `+`, `-`, and `/`. Empty, dot, and parent components are forbidden. Tabs, newlines, backslashes, and other characters are unsupported. Regular files are recorded; directories are containers only. Symlinks, hard-linked files, devices, sockets, and FIFOs are unsupported. Ordinary file permissions (0000–0777) are recorded. Set-ID/sticky bits are rejected. Owner/group, ACLs, xattrs, directory modes, empty directories, and configuration semantics are not recorded.

## Record format

Records use literal tabs and end in a newline. Fixed header rows precede build evidence, then sorted unique dependency rows, then sorted unique file rows:

```text
format<TAB>pkg-state-v2
package<TAB>NAME<TAB>VERSION
build-record<TAB>SHA256-OF-CANONICAL-BUILD-RECORD
evidence<TAB>record_type<TAB>build
...all 19 build-output keys in their canonical order...
dependency<TAB>DEPENDENCY-NAME
file<TAB>SHA256<TAB>DECIMAL-SIZE<TAB>RELATIVE-PATH<TAB>FOUR-DIGIT-OCTAL-MODE
```

The complete embedded evidence order is defined in `mk/state-schema.awk` and matches `mk/verify-metadata.sh build-record` output: record type, origin, namespace, identity, recipe, source hash, manifest hash, material/SBOM references, builder/phase/command labels, and advisory-result fields. Unknown, missing, duplicate, reordered, or malformed fields are rejected. No record content is sourced or evaluated as shell code.

Registration recomputes the stage manifest and requires byte equality with the supplied manifest. It validates the build-output schema and package identity, reconstructs its exact canonical bytes, and binds its `manifest_hash` to those file rows. Both the manifest and embedded build fingerprints are rechecked whenever records are loaded. The build evidence remains advisory; registration does not re-execute the build or re-resolve its source references. Neither self-consistent records nor their hashes establish authenticity, reproducibility, or binary eligibility.

Dependencies name already registered packages (or the candidate itself). Duplicate ownership and file-as-directory conflicts are rejected across all logical package paths, even though package stages are physically separate. No version constraints or solver are implemented. Identical re-registration succeeds without writing; different evidence for an existing name is rejected. Updates need a separate future contract.

Publication copies a fully validated candidate into an adjacent temporary file and renames it into place. Tested validation and publication failures preserve previous records. Registered stages are protected from subsequent make build/clean operations; editing payload manually is still detectable by verification. Single-writer operation is required. This is not hostile-process isolation, a multi-record transaction, or power-loss durability.

## Editable world and derived views

`world` and registration's dependency file accept one exact package ID per line, blank lines, and full-line `#` comments. Duplicate names are rejected; input order is immaterial. Unknown world roots or dangling dependencies block views. Dependency input is canonicalized during registration; `world` is never rewritten by the tool.

Output is sorted under `LC_ALL=C`:

| Command | Rows (tab-separated) |
| --- | --- |
| `list` | name, version, `explicit` if in world or `dependency` otherwise |
| `owners` | logical path, owning package |
| `files NAME` | logical path, hash, size, mode (`untracked` for v1) |
| `deps NAME` / `rdeps NAME` | direct dependency / direct dependent name |
| `orphans` | `report orphan-plan-v1 non-deleting` header; then `orphan NAME` rows |

An unrooted package is labeled `dependency` in the list even when it is an orphan. Orphan reporting computes the transitive closure of `world`, including cycles. It prints candidates only; no apply, remove, prune, or delete operation exists. Orphan reports depend on record/root integrity, not current payload health; use `verify` separately.

## Verification

`verify` checks only registered package stages, without repair or mutation. It reports `missing`, `content-mismatch`, `size-mismatch`, `type-mismatch`, `unreadable`, `mode-mismatch`, `unsupported-mode`, `mode-untracked`, and `unowned` file discrepancies. Unsafe entry names, missing stage roots, traversal failures, and hard links yield `unsupported-or-missing-stage`; symlinks/special entries yield `unsupported-type`, without following them. A damaged package stage is skipped if safely inspecting its files is impossible.

Successful verification emits `verified staged-regular-files`. Discrepancies produce sorted rows and exit nonzero. Corrupt records, ownership conflicts, invalid world, and dangling dependencies fail before payload inspection. Files outside registered stages are not inventoried. This is staged-payload verification, not a claim about a live installation or full filesystem metadata.

## Runnable hello-local example

Run from the repository root. The evidence generator currently requires repository-relative references, so this example creates its private root beneath the checkout:

```sh
fixture_root=$(mktemp -d "$PWD/.pkg-mgr-demo.XXXXXX")
make -f mk/pkg.mk ROOT="$fixture_root" init-root
make -j8 -f mk/pkg.mk ROOT="$fixture_root" package
mkdir "$fixture_root/evidence"
sh mk/verify-metadata.sh manifest "$fixture_root/stage/hello-local" "$fixture_root/evidence/manifest.tsv"
MANIFEST_REF="${fixture_root#"$PWD/"}/evidence/manifest.tsv" awk '
    /^manifest_ref=/ {print "manifest_ref=" ENVIRON["MANIFEST_REF"]; next}
    {print}
' fixtures/metadata-boundary/build-input.kv > "$fixture_root/evidence/input.kv"
sh mk/verify-metadata.sh build-record "$fixture_root/evidence/input.kv" "$fixture_root/evidence/build.kv"
: > "$fixture_root/evidence/deps"
sh mk/state.sh init "$fixture_root"
sh mk/state.sh register "$fixture_root" "$fixture_root/evidence/manifest.tsv" "$fixture_root/evidence/build.kv" "$fixture_root/evidence/deps"
printf 'hello-local\n' > "$fixture_root/state/world"
sh mk/state.sh list "$fixture_root"
sh mk/state.sh owners "$fixture_root"
sh mk/state.sh verify "$fixture_root"
sh mk/state.sh orphans "$fixture_root"
```

Keep the root for inspection. There is intentionally no state-removal command. The test harness cleans only its own disposable fixtures.

## Permission schema and compatibility

New registrations use `pkg-state-v2` and observe file modes with `mk/file-mode.sh`, which supports BSD and GNU `stat` syntax and fails if the mode cannot be read or contains unsupported bits. Registration does not chmod payload. Permissions are local registration observations; the existing content manifest/build hash format remains unchanged and does not attest those observations. Binary v2 descriptors bind the full record, including modes.

V1 records remain valid for inspection and graph queries. Verification reports `mode-untracked` and exits nonzero for their files. No migration infers expected permissions from potentially changed payload or rewrites old records. Rebuild/register into a fresh private root for v2 transport. Existing records, dependency fingerprints and saved historical evidence remain untouched. Mixed-version inspection is supported; transport requires the root to pass full verification.

A re-registration with changed permissions is different evidence and is refused. `check-register` performs the same validation without publishing. Verification never chmods or repairs files. Readability is still required for content verification, so a recorded mode does not promise that every possible permission setting can be transported by an unprivileged caller.
