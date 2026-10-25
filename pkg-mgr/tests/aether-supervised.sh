#!/bin/sh
# Validate host transport only; synthetic inputs are not a native boot witness.
set -eu
repo=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
exec python3 "$repo/tests/aether-supervised.py"
