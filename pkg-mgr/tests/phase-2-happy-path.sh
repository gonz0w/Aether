#!/bin/sh
set -eu

expected_phases='fetch-start fetch-complete verify-start verify-complete extract-start extract-complete patch-start patch-complete configure-start configure-complete build-start build-complete test-start test-complete stage-install-start stage-install-complete manifest-start manifest-complete'

fail() {
    printf '%s\n' "$1" >&2
    exit 1
}

assert_file() {
    test -f "$1" || fail "missing expected file: $1"
}

root=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-happy.XXXXXX")
root=$(CDPATH='' cd "$root" && pwd -P)
trap 'rm -rf "$root"' 0
trap 'exit 1' HUP INT TERM
make -s -f mk/pkg.mk ROOT="$root" init-root
make -s -f mk/pkg.mk ROOT="$root" package
cd "$root"

assert_file distfiles/hello-local.txt
assert_file work/hello-local/hello.txt
assert_file work/hello-local/build/hello.txt
assert_file stage/hello-local/usr/local/share/hello-local/hello.txt
assert_file manifests/hello-local.manifest
assert_file logs/hello-local/phase.log

actual_phases=$(tr '\n' ' ' < logs/hello-local/phase.log | sed 's/[[:space:]]*$//')
test "$actual_phases" = "$expected_phases" || fail "unexpected phase log: $actual_phases"

manifest=$(cat manifests/hello-local.manifest)
test "$manifest" = 'usr/local/share/hello-local/hello.txt' || fail "unexpected manifest: $manifest"
