#!/bin/sh
# Development-only offline gate; never fetch or follow a moving sibling release.
set -eu
repo=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
command -v python3 >/dev/null 2>&1 || {
    printf 'standards-check: python3 is required for development validation\n' >&2
    exit 1
}
for checker in check-experience.py check-standards.py check-distribution.py; do
    python3 "$repo/docs/$checker"
done
printf 'All three pinned standards checks passed (not runtime conformance).\n'
