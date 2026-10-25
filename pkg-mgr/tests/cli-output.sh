#!/bin/sh
# Development-only pipe/process driver; package runtime remains POSIX shell.
set -eu
repo=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
exec python3 "$repo/tests/cli-output.py"
