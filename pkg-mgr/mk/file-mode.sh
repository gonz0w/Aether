#!/bin/sh
# Read ordinary permission bits using BSD or GNU stat; never infer from access.
set -eu
LC_ALL=C
export LC_ALL
test "$#" -eq 1 && test -f "$1" && ! test -L "$1" || exit 1
if mode=$(stat -f '%Lp' "$1" 2>/dev/null) && test -n "$mode"; then :
else mode=$(stat -c '%a' "$1")
fi
case $mode in
    [0-7]) mode=000$mode ;;
    [0-7][0-7]) mode=00$mode ;;
    [0-7][0-7][0-7]) mode=0$mode ;;
    0[0-7][0-7][0-7]) ;;
    *) printf 'mode-error: unsupported permission bits\n' >&2; exit 1 ;;
esac
printf '%s\n' "$mode"
