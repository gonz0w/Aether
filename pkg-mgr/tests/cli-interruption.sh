#!/bin/sh
# Python drives isolated process-group signals; it is not a runtime dependency.
set -eu
repo=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
exec python3 "$repo/tests/cli-interruption.py"
