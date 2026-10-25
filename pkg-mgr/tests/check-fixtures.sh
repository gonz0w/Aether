#!/bin/sh
# Run the active fixture checks without cleaning outputs in the working checkout.
set -eu
repo_root=$(CDPATH='' cd "$(dirname "$0")/.." && pwd)
sh "$repo_root/tests/check-standards.sh"
python3 "$repo_root/tests/check-development.py" --lint-all
python3 "$repo_root/tests/check-coverage-fixtures.py"
python3 "$repo_root/tests/cli-dispatch.py"
python3 "$repo_root/tests/check-source-snapshot-fixtures.py"
python3 "$repo_root/tests/check-watchdog-fixtures.py"
python3 "$repo_root/tests/sdk-profile.py"
python3 "$repo_root/tests/sdk-transport.py"
python3 "$repo_root/tests/sdk-rebuild-plan.py"
python3 "$repo_root/tests/check-manuals.py"
python3 "$repo_root/tests/origins-source-handoff.py"
python3 "$repo_root/tests/origins-source-records.py"
python3 "$repo_root/tests/origins-closure-cases.py"
test_root=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-check.XXXXXX")
trap 'rm -rf "$test_root"' 0
trap 'exit 1' HUP INT TERM
for directory in bin mk recipes fixtures manifests tests; do
    cp -R "$repo_root/$directory" "$test_root/"
done
cd "$test_root"
# Run each local fixture once; test-owned temporary roots keep outputs isolated.
for test_file in \
    tests/distinfo-parser-fixtures.sh \
    tests/phase-2-happy-path.sh \
    tests/phase-3-safety-failure.sh \
    tests/package-boundary.sh \
    tests/package-state.sh \
    tests/aether-boot.sh \
    tests/aether-boot-v2.sh \
    tests/aether-supervised.sh \
    tests/source-recipes.sh \
    tests/cli.sh \
    tests/cli-interruption.sh \
    tests/cli-output.sh \
    tests/binary-package.sh \
    tests/trust-metadata-source.sh \
    tests/trust-metadata-snapshot.sh \
    tests/trust-metadata-records.sh
do
    printf '\nRunning %s\n' "$test_file"
    sh "$test_file"
done
printf '\nAll sixteen active fixture tests passed.\n'
