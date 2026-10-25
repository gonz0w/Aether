#!/bin/sh
set -eu

fail() {
    printf '%s\n' "$1" >&2
    exit 1
}

root=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-safety.XXXXXX")
root=$(CDPATH='' cd "$root" && pwd -P)
trap 'rm -rf "$root"' 0
trap 'exit 1' HUP INT TERM
make -s -f mk/pkg.mk ROOT="$root" init-root
cleanup_outputs() {
    make -s -f mk/pkg.mk ROOT="$root" clean
}

assert_file() {
    test -f "$1" || fail "missing expected file: $1"
}

assert_no_file() {
    test ! -e "$1" || fail "unexpected file exists: $1"
}

assert_log_has() {
    token=$1
    grep -qx "$token" "$root/logs/hello-local/phase.log" || fail "missing log token: $token"
}

assert_log_lacks() {
    token=$1
    ! grep -qx "$token" "$root/logs/hello-local/phase.log" || fail "unexpected log token: $token"
}

assert_manifest() {
    expected=$1
    actual=$(cat "$root/manifests/hello-local.manifest")
    test "$actual" = "$expected" || fail "unexpected manifest: $actual"
}

assert_manifest_block() {
    expected=$1
    actual=$(cat "$root/manifests/hello-local.manifest")
    test "$actual" = "$expected" || fail "unexpected manifest block: $actual"
}

final_prefix=$root/unwritten-prefix
staged_prefix="$root/stage/hello-local$final_prefix"

cleanup_outputs
make -f mk/pkg.mk ROOT="$root" PREFIX="$final_prefix" package >/dev/null
assert_file "$staged_prefix/share/hello-local/hello.txt"
assert_no_file "$final_prefix/share/hello-local/hello.txt"
assert_manifest "${final_prefix#/}/share/hello-local/hello.txt"

mkdir -p "$staged_prefix/share/hello-local/docs" "$staged_prefix/share/hello-local/bin"
printf '%s\n' alpha > "$staged_prefix/share/hello-local/docs/A.txt"
printf '%s\n' beta > "$staged_prefix/share/hello-local/bin/z.txt"
make -f mk/pkg.mk ROOT="$root" PREFIX="$final_prefix" manifest >/dev/null
assert_manifest_block "${final_prefix#/}/share/hello-local/bin/z.txt
${final_prefix#/}/share/hello-local/docs/A.txt
${final_prefix#/}/share/hello-local/hello.txt"

cleanup_outputs
if make -f mk/pkg.mk ROOT="$root" PREFIX="$final_prefix" FAIL_PHASE=verify package >/dev/null 2>&1; then
    fail 'verify failure fixture unexpectedly succeeded'
fi
assert_file "$root/logs/hello-local/phase.log"
assert_log_has verify-start
assert_log_has verify-failure
for token in extract-start configure-start build-start stage-install-start manifest-start manifest-complete package-success source-authenticity; do
    assert_log_lacks "$token"
done
assert_no_file "$staged_prefix/share/hello-local/hello.txt"
assert_no_file "$final_prefix/share/hello-local/hello.txt"
assert_no_file "$root/manifests/hello-local.manifest"

cleanup_outputs
if make -f mk/pkg.mk ROOT="$root" PREFIX="$final_prefix" FAIL_PHASE=build package >/dev/null 2>&1; then
    fail 'build failure fixture unexpectedly succeeded'
fi
assert_file "$root/logs/hello-local/phase.log"
assert_log_has build-start
assert_log_has build-failure
for token in stage-install-start stage-install-complete manifest-start manifest-complete package-success source-authenticity; do
    assert_log_lacks "$token"
done
assert_no_file "$staged_prefix/share/hello-local/hello.txt"
assert_no_file "$final_prefix/share/hello-local/hello.txt"
assert_no_file "$root/manifests/hello-local.manifest"

cleanup_outputs
