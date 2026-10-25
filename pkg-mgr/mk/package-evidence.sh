#!/bin/sh
# Bridge the real recipes to the existing advisory build-record schema.
set -eu
repo=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
sh "$repo/mk/check-root.sh" check
verifier=$repo/mk/verify-metadata.sh
recipe=$repo/recipes/$PKGNAME
hash() { sh "$verifier" hash-file "$1"; }
fail() { printf 'package-evidence: %s\n' "$*" >&2; exit 1; }
case ${1-} in
    host)
        target=$DESTDIR$PREFIX/share/pkg-mgr/$PKGNAME
        mkdir -p "$target"
        temporary=$(mktemp "$target/host.kv.XXXXXX")
        trap 'rm -f "$temporary"' 0
        trap 'exit 1' HUP INT TERM
        host_os=$(uname -s); host_arch=$(uname -m)
        compiler_target=$("$CC" -dumpmachine)
        compiler_version=$("$CC" --version)
        recipe_digest=$(hash "$recipe/package.mk")
        phase_digest=$(hash "$recipe/phases.sh")
        driver_digest=$(hash "$repo/mk/pkg.mk")
        helper_digest=$(hash "$repo/mk/package-evidence.sh")
        {
            printf 'format=host-build-observation-v1\nhost_os=%s\nhost_arch=%s\n' "$host_os" "$host_arch"
            printf 'compiler_target=%s\ncompiler_command=%s\n' "$compiler_target" "$CC"
            printf '%s\n' "$compiler_version" | sed -n '1s/^/compiler_version=/p'
            printf 'optimization=-O2\ntarget_runtime=host-only\naether_compatibility=not-proven\n'
            printf 'recipe_sha256=%s\nphase_script_sha256=%s\n' "$recipe_digest" "$phase_digest"
            printf 'make_driver_sha256=%s\nevidence_helper_sha256=%s\n' "$driver_digest" "$helper_digest"
            while IFS= read -r dependency; do
                test -n "$dependency" || continue
                dependency_digest=$(hash "$ROOT/state/packages/$dependency.tsv")
                printf 'dependency_%s_record_sha256=%s\n' "$dependency" "$dependency_digest"
            done < "$recipe/dependencies"
        } > "$temporary"
        mv "$temporary" "$target/host.kv"
        ;;
    record)
        physical=$(CDPATH='' cd "$ROOT" && pwd -P)
        case $physical in "$repo"/*) relative=${physical#"$repo/"} ;; *) fail 'evidence currently requires ROOT beneath the repository' ;; esac
        evidence=$ROOT/evidence/$PKGNAME
        mkdir -p "$evidence"
        source_ref=$relative/distfiles/$DISTNAME
        SOURCE_REF=$source_ref awk '
            /^source_uri=/ {print "source_uri=file:" ENVIRON["SOURCE_REF"]; next}
            /^source_kind=/ {print "source_kind=local-file"; next}
            {print}' "$SOURCE_METADATA" > "$evidence/source.kv"
        sh "$verifier" verify-source "$evidence/source.kv" "$DISTFILE"
        sh "$verifier" manifest "$STAGEDIR" "$evidence/manifest.tsv"
        digest=$(hash "$DISTFILE")
        {
            printf 'SPDXVersion: SPDX-2.3\nDataLicense: CC0-1.0\nSPDXID: SPDXRef-DOCUMENT\n'
            printf 'DocumentName: %s-advisory\nDocumentNamespace: https://example.invalid/pkg-mgr/%s/advisory\n' "$PKGNAME" "$PKGNAME"
            printf 'Creator: Tool: pkg-mgr-prototype\nCreated: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
            printf 'PackageName: %s\nSPDXID: SPDXRef-Package-%s\nPackageVersion: %s\n' "$PKGNAME" "$PKGNAME" "$PKGVERSION"
            printf 'PackageDownloadLocation: NOASSERTION\nFilesAnalyzed: false\nPackageChecksum: SHA256: %s\n' "$digest"
            printf 'PackageLicenseConcluded: NOASSERTION\nPackageLicenseDeclared: NOASSERTION\nPackageCopyrightText: NOASSERTION\n'
            printf 'Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-Package-%s\n' "$PKGNAME"
        } > "$evidence/advisory.spdx"
        {
            printf 'record_type=build\nrepo_origin=file:pkg-mgr-recipes\nnamespace=host-prototype\npackage_name=%s\nversion=%s\n' "$PKGNAME" "$PKGVERSION"
            printf 'recipe_path=recipes/%s/package.mk\nrecipe_revision=sha256:%s\n' "$PKGNAME" "$(hash "$recipe/package.mk")"
            printf 'source_hash_alg=sha256\nsource_hash=%s\nmanifest_ref=%s/evidence/%s/manifest.tsv\n' "$digest" "$relative" "$PKGNAME"
            printf 'materials_ref=%s/evidence/%s/source.kv\nmaterial_path=%s\nsbom_ref=%s/evidence/%s/advisory.spdx\n' "$relative" "$PKGNAME" "$source_ref" "$relative" "$PKGNAME"
            printf 'builder_label=host-fixture\nphase_label=package\ncommand_label=make-register\nprovenance_confidence=advisory\nverification_result=warn\nresult_label=reproducible-build-success-not-proven\n'
        } > "$evidence/input.kv"
        sh "$verifier" build-record "$evidence/input.kv" "$evidence/build.kv"
        sh "$verifier" check-sbom "$evidence/advisory.spdx"
        ;;
    register)
        if test ! -e "$ROOT/state"; then sh "$repo/mk/state.sh" init "$ROOT"; fi
        sh "$repo/mk/state.sh" register "$ROOT" "$ROOT/evidence/$PKGNAME/manifest.tsv" "$ROOT/evidence/$PKGNAME/build.kv" "$recipe/dependencies"
        ;;
    *) exit 64 ;;
esac
