#!/bin/sh
# SPDX-License-Identifier: BSD-2-Clause
# Default development entry: owned process group, 600-second limit, retained logs.
set -eu
repo_root=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
exec python3 "$repo_root/tests/check-watchdog.py"
