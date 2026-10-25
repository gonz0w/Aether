#!/bin/sh
# REQ-009 / REQ-008 distinfo parser semantics fixture.
#
# This script is intentionally self-contained: it models parser input/output
# strings and fail-closed decisions only. It performs no network fetch, real
# package extract, configure, build, stage, install, manifest, source
# authenticity, dependency solver, or final-prefix work.

set -eu

extract_attempted=false
build_attempted=false
stage_attempted=false
manifest_claimed=false
source_authenticity_claimed=false

fail() {
  printf '%s\n' "FAIL: $*" >&2
  exit 1
}

assert_eq() {
  actual=$1
  expected=$2
  label=$3
  [ "$actual" = "$expected" ] || fail "$label: expected '$expected', got '$actual'"
}

assert_no_downstream_claims() {
  [ "$extract_attempted" = false ] || fail "$1: did not stop before extract"
  [ "$build_attempted" = false ] || fail "$1: build claim must be absent"
  [ "$stage_attempted" = false ] || fail "$1: stage claim must be absent"
  [ "$manifest_claimed" = false ] || fail "$1: manifest claim must be absent"
  [ "$source_authenticity_claimed" = false ] || fail "$1: source-authenticity claim must be absent"
}

is_sha256_hex() {
  case $1 in
    *[!0123456789abcdef]*|'') return 1 ;;
  esac
  [ ${#1} -eq 64 ]
}

distinfo_digest_for() {
  # Parse canonical REQ-008 distinfo rows: SHA256 (filename) = hex
  file=$1
  expected_name=$2
  matches=0
  digest=''

  while IFS= read -r line || [ -n "$line" ]; do
    [ -n "$line" ] || continue
    case $line in
      "SHA256 ("*") = "*) ;;
      *) return 10 ;; # malformed
    esac
    name=${line#SHA256 (}
    name=${name%%) = *}
    value=${line##*) = }
    is_sha256_hex "$value" || return 11
    if [ "$name" = "$expected_name" ]; then
      matches=$((matches + 1))
      if [ -z "$digest" ]; then
        digest=$value
      elif [ "$digest" != "$value" ]; then
        return 12 # conflicting
      fi
    fi
  done < "$file"

  [ "$matches" -gt 0 ] || return 13 # missing expected filename
  printf '%s\n' "$digest"
}

parse_hash_output() {
  # Accepted REQ-009 Phase 1 parser modes:
  # - sha256sum-first-field
  # - bsd-sha256-named
  # - openssl-dgst-sha256
  mode=$1
  expected_name=$2
  line=$3

  case $mode in
    sha256sum-first-field)
      digest=${line%%[  ]*}
      rest=${line#*"$digest"}
      case $rest in
        *"$expected_name"*) ;;
        *) return 23 ;; # filename mismatch / missing binding
      esac
      ;;
    bsd-sha256-named)
      case $line in
        "SHA256 ($expected_name) = "*) digest=${line##*) = } ;;
        "SHA256 ("*") = "*) return 23 ;; # filename mismatch
        *) return 20 ;; # malformed
      esac
      ;;
    openssl-dgst-sha256)
      case $line in
        "SHA256($expected_name)= "*) digest=${line##*= } ;;
        "SHA256("*")= "*) return 23 ;; # filename mismatch
        *) return 20 ;; # malformed
      esac
      ;;
    *) return 24 ;;
  esac

  is_sha256_hex "$digest" || return 21
  printf '%s\n' "$digest"
}

verify_before_extract() {
  distinfo=$1
  expected_name=$2
  mode=$3
  actual_output=$4
  expected_digest=$(distinfo_digest_for "$distinfo" "$expected_name") || return 30
  actual_digest=$(parse_hash_output "$mode" "$expected_name" "$actual_output") || return 31
  [ "$expected_digest" = "$actual_digest" ] || return 32 # digest mismatch
}

with_fixture() {
  file=$(mktemp "${TMPDIR:-/tmp}/distinfo-fixture.XXXXXX")
  printf '%s\n' "$2" > "$file"
  "$1" "$file"
  rc=$?
  rm -f "$file"
  return "$rc"
}

good_digest=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
other_digest=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
short_digest=aaaaaaaa
long_digest=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
expected_name=hello-2.12.3.tar.gz
canonical_row="SHA256 ($expected_name) = $good_digest"

check_success_modes() {
  distinfo=$1
  assert_eq "$(parse_hash_output sha256sum-first-field "$expected_name" "$good_digest  $expected_name")" "$good_digest" "sha256sum-first-field parser mode"
  assert_eq "$(parse_hash_output bsd-sha256-named "$expected_name" "SHA256 ($expected_name) = $good_digest")" "$good_digest" "bsd-sha256-named parser mode"
  assert_eq "$(parse_hash_output openssl-dgst-sha256 "$expected_name" "SHA256($expected_name)= $good_digest")" "$good_digest" "openssl-dgst-sha256 parser mode"
  verify_before_extract "$distinfo" "$expected_name" sha256sum-first-field "$good_digest  $expected_name"
  verify_before_extract "$distinfo" "$expected_name" bsd-sha256-named "SHA256 ($expected_name) = $good_digest"
  verify_before_extract "$distinfo" "$expected_name" openssl-dgst-sha256 "SHA256($expected_name)= $good_digest"
}

check_distinfo_negative_cases() {
  # malformed distinfo must fail closed before extract.
  malformed=$(mktemp "${TMPDIR:-/tmp}/distinfo-malformed.XXXXXX")
  printf '%s\n' "malformed row for $expected_name $good_digest" > "$malformed"
  if verify_before_extract "$malformed" "$expected_name" bsd-sha256-named "SHA256 ($expected_name) = $good_digest"; then
    fail "malformed distinfo unexpectedly passed"
  fi
  rm -f "$malformed"
  assert_no_downstream_claims "malformed distinfo"

  missing=$(mktemp "${TMPDIR:-/tmp}/distinfo-missing.XXXXXX")
  printf '%s\n' "SHA256 (zlib-1.3.2.tar.gz) = $good_digest" > "$missing"
  if verify_before_extract "$missing" "$expected_name" bsd-sha256-named "SHA256 ($expected_name) = $good_digest"; then
    fail "missing expected filename unexpectedly passed"
  fi
  rm -f "$missing"
  assert_no_downstream_claims "missing expected filename"

  conflicting=$(mktemp "${TMPDIR:-/tmp}/distinfo-conflicting.XXXXXX")
  printf '%s\n%s\n' "SHA256 ($expected_name) = $good_digest" "SHA256 ($expected_name) = $other_digest" > "$conflicting"
  if verify_before_extract "$conflicting" "$expected_name" bsd-sha256-named "SHA256 ($expected_name) = $good_digest"; then
    fail "multiple conflicting matches unexpectedly passed"
  fi
  rm -f "$conflicting"
  assert_no_downstream_claims "multiple conflicting matches"

  missing_file=$(mktemp "${TMPDIR:-/tmp}/distinfo-missing-file.XXXXXX")
  rm -f "$missing_file"
  if verify_before_extract "$missing_file" "$expected_name" bsd-sha256-named "SHA256 ($expected_name) = $good_digest" 2>/dev/null; then
    fail "missing distfile metadata unexpectedly passed"
  fi
  assert_no_downstream_claims "missing distfile"
}

check_hash_output_negative_cases() {
  distinfo=$1
  for output in \
    "not a hash line" \
    "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz  $expected_name" \
    "$short_digest  $expected_name" \
    "$long_digest  $expected_name" \
    "$good_digest  zlib-1.3.2.tar.gz" \
    "$other_digest  $expected_name"
  do
    if verify_before_extract "$distinfo" "$expected_name" sha256sum-first-field "$output"; then
      fail "negative parser/hash case unexpectedly passed: $output"
    fi
    assert_no_downstream_claims "parser output or digest mismatch"
  done

  if verify_before_extract "$distinfo" "$expected_name" bsd-sha256-named "SHA256 (zlib-1.3.2.tar.gz) = $good_digest"; then
    fail "bsd filename mismatch unexpectedly passed"
  fi
  assert_no_downstream_claims "filename mismatch"

  if verify_before_extract "$distinfo" "$expected_name" openssl-dgst-sha256 "SHA256(zlib-1.3.2.tar.gz)= $good_digest"; then
    fail "openssl filename mismatch unexpectedly passed"
  fi
  assert_no_downstream_claims "filename mismatch"
}

main() {
  canonical=$(mktemp "${TMPDIR:-/tmp}/distinfo-canonical.XXXXXX")
  printf '%s\n' "$canonical_row" > "$canonical"
  check_success_modes "$canonical"
  check_distinfo_negative_cases
  check_hash_output_negative_cases "$canonical"
  rm -f "$canonical"
  assert_no_downstream_claims "successful parser fixture still has no downstream claims"
  printf '%s\n' "REQ-009/REQ-008 distinfo parser fixture semantics passed before extract"
}

main "$@"
