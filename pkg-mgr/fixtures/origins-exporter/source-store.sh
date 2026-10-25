#!/bin/sh
# SPDX-License-Identifier: BSD-2-Clause
set -eu
if ! command -v python3 >/dev/null 2>&1; then
    printf '%s\n' '[BLOCKED] ORIGINS-TOOL-UNAVAILABLE: Python 3 is required.' >&2
    exit 2
fi
script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$script_dir/source_store.py" "$@"
