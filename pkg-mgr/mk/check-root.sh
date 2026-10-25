#!/bin/sh
# Accidental-path boundary for a caller-owned fixture, not hostile-process isolation.
set -eu
LC_ALL=C
export LC_ALL
fail() { printf 'unsafe fixture root: %s\n' "$*" >&2; exit 1; }
case ${1-} in init|check|state|replacement) action=$1 ;; *) exit 64 ;; esac
root=${ROOT-}
case $root in /*) ;; *) fail 'ROOT must be an absolute path to an existing private directory' ;; esac
case $root in */) fail 'ROOT must not have a trailing slash' ;; esac
case "$root/" in *'/../'*|*'/./'*) fail 'ROOT must not contain dot or parent components' ;; esac
case $root in *"
"*|*"$(printf '\t')"*) fail 'ROOT cannot contain tabs or newlines' ;; esac
if ! { test -d "$root" && ! test -L "$root"; }; then fail 'ROOT must be a real directory'; fi
physical=$(CDPATH='' cd "$root" && pwd -P)
home_physical=$(CDPATH='' cd "$HOME" && pwd -P)
case $physical in /|/usr|/usr/local|/etc|/private/etc|/var|/private/var|/tmp|/private/tmp|/opt|/home|/Users) fail 'system directory' ;; esac
if ! { test "$physical" != "$home_physical" && test "$physical" != "$(pwd -P)"; }; then fail 'HOME and the working directory are not fixture roots'; fi
# POSIX ls -n exposes numeric owner and permission bits on the directory itself.
attributes=$(ls -nd "$root") || fail 'cannot inspect ROOT'
access_mode=$(printf '%s\n' "$attributes" | awk '{print $1}')
case $access_mode in *+*) fail 'extended ROOT ACLs are unsupported' ;; esac
permissions=$(printf '%s\n' "$attributes" | awk '{print substr($1,1,10)}')
owner=$(printf '%s\n' "$attributes" | awk '{print $3}')
if ! { test "$permissions" = drwx------ && test "$owner" = "$(id -u)"; }; then fail 'ROOT must be owned by the caller with mode 0700'; fi

if test "$action" != replacement && { test -e "$root/.replacement" || test -L "$root/.replacement"; }; then
    fail 'replacement pending; use replacement.sh finish with the intent digest'
fi
if test "$action" != state && test "$action" != replacement; then
pkg=${PKGNAME-}
case $pkg in ''|[!a-zA-Z0-9]*|*[!a-zA-Z0-9._+-]*) fail 'invalid PKGNAME' ;; esac
# A recipe selects one source basename; it cannot redirect outputs outside ROOT.
distname=${DISTNAME:-hello-local.txt}
case $distname in ''|[!A-Za-z0-9]*|*[!A-Za-z0-9._+-]*) fail 'invalid DISTNAME' ;; esac
test "${DISTDIR-}" = "$root/distfiles" &&
test "${DISTFILE-}" = "$root/distfiles/$distname" &&
test "${WRKDIR-}" = "$root/work/$pkg" &&
test "${STAGEDIR-}" = "$root/stage/$pkg" &&
test "${DESTDIR-}" = "$root/stage/$pkg" &&
test "${MANIFEST-}" = "$root/manifests/$pkg.manifest" &&
test "${LOGDIR-}" = "$root/logs/$pkg" || fail 'output overrides must match the fixed ROOT layout'
case ${PREFIX-} in /*) ;; *) fail 'PREFIX must be absolute within the stage' ;; esac
case "$PREFIX/" in *'/../'*|*'/./'*|*'//'*) fail 'PREFIX must not contain empty, dot, or parent components' ;; esac
case $PREFIX in *"
"*|*"$(printf '\t')"*) fail 'PREFIX cannot contain tabs or newlines' ;; esac

fi

marker=$root/.pkg-mgr-root
if test "$action" = init; then
    contents=$(find "$root/." ! -name . -print) || fail 'cannot inspect directory contents'
    test -z "$contents" || fail 'initialization requires an empty directory'
    (umask 077; set -C; printf '%s\n' pkg-mgr-fixture-v1 > "$marker")
    exit
fi
# State readers validate their authority files separately and classify payload
# damage without following links. They do not mutate the build/stage tree.
if test "$action" = state || test "$action" = replacement; then
    if ! { test -f "$marker" && ! test -L "$marker"; }; then fail 'missing regular fixture marker'; fi
    test "$(cat "$marker")" = pkg-mgr-fixture-v1 || fail 'invalid fixture marker'
    exit
fi
# Reject links (including hard links) and non-regular payloads before mutation.
# Explicit -print on both branches avoids find's implicit-print differences.
bad=$(find "$root" \( ! -type d ! -type f \) -print -o \( -type f -links +1 \) -print) || fail 'cannot inspect fixture tree'
test -z "$bad" || fail 'symlinks, special files, and hard-linked files are unsupported'
test -f "$marker" || fail 'run init-root on an empty private directory first'
test "$(cat "$marker")" = pkg-mgr-fixture-v1 || fail 'invalid fixture marker'
# Registration turns this stage into observed package state. Build/clean helpers
# must not silently replace or remove it; update/remove is a later contract.
test ! -e "$root/state/packages/$pkg.tsv" || fail 'registered package stage cannot be rebuilt or cleaned'
