#!/bin/sh
set -eu

usage() {
    printf '%s\n' "usage: $0 <ensure-dirs|log|phase|manifest> [message]" >&2
    exit 64
}

# Every helper entry rechecks the fixture before making directories or logs.
script_dir=$(CDPATH='' cd "$(dirname "$0")" && pwd -P)
sh "$script_dir/check-root.sh" check


ensure_dirs() {
    mkdir -p "$DISTDIR" "$WRKDIR" "$STAGEDIR" "$(dirname "$MANIFEST")" "$LOGDIR"
}

append_log() {
    ensure_dirs
    message=${1:-scaffold helper invoked}
    printf '%s\n' "$message" >> "$LOGDIR/phase.log"
}

log_phase() {
    phase_name=${1:?phase name required}
    phase_state=${2:?phase state required}
    case "$phase_state" in
        start|complete|failure)
            append_log "$phase_name-$phase_state"
            ;;
        *)
            printf '%s\n' "unknown phase state: $phase_state" >&2
            exit 64
            ;;
    esac
}

case "${1-}" in
    ''|-h|--help)
        usage
        ;;
    ensure-dirs)
        ensure_dirs
        ;;
    log)
        shift
        append_log "${1:-scaffold helper invoked}"
        ;;
    manifest)
        # Check each stage entry through the existing hash manifest generator;
        # project its validated rows to paths, then publish only complete output.
        temporary=$(mktemp "$MANIFEST.tmp.XXXXXX")
        trap 'rm -f "$temporary" "$temporary.hashes"' 0
        trap 'exit 1' HUP INT TERM
        sh "$script_dir/verify-metadata.sh" manifest "$STAGEDIR" "$temporary.hashes" >/dev/null
        cut -f3 "$temporary.hashes" > "$temporary"
        mv "$temporary" "$MANIFEST"
        ;;
    phase)
        shift
        test "$#" -eq 2 || usage
        log_phase "$1" "$2"
        ;;
    *)
        printf '%s\n' "unknown helper: $1" >&2
        exit 64
        ;;
esac
