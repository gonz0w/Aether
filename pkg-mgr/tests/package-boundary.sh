#!/bin/sh
# End-to-end ordering, copied-input integrity, and private output-root boundaries.
set -eu
scratch=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-boundary.XXXXXX")
scratch=$(CDPATH='' cd "$scratch" && pwd -P)
trap 'rm -rf "$scratch"' 0
trap 'exit 1' HUP INT TERM
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }
pm() { make -s -f mk/pkg.mk ROOT="$root" "$@"; }
reject() {
    if pm "$@" > "$scratch/rejected.log" 2>&1; then fail "unexpected success: $*"; fi
}
new_root() {
    root=$scratch/$1
    (umask 077; mkdir "$root")
    pm init-root
}
new_root "output with spaces and 'quote"
pm -j1 package > "$scratch/serial.out"
cp "$root/logs/hello-local/phase.log" "$scratch/serial.log"
cp "$root/manifests/hello-local.manifest" "$scratch/serial.manifest"
cp "$root/stage/hello-local/usr/local/share/hello-local/hello.txt" "$scratch/payload"
pm clean
pm -j8 package build manifest > "$scratch/parallel.out"
cmp "$scratch/serial.log" "$root/logs/hello-local/phase.log"
cmp "$scratch/serial.manifest" "$root/manifests/hello-local.manifest"
cmp "$scratch/payload" "$root/stage/hello-local/usr/local/share/hello-local/hello.txt"
reject FAIL_PHASE=build package
cmp "$scratch/payload" "$root/stage/hello-local/usr/local/share/hello-local/hello.txt"
cmp "$scratch/serial.manifest" "$root/manifests/hello-local.manifest"
reject -j8 clean package
reject init-root package
cmp "$scratch/payload" "$root/stage/hello-local/usr/local/share/hello-local/hello.txt"

# Corrupt only the fetched copy, after cp succeeds. The original source stays valid.
mkdir "$scratch/bin"
real_cp=$(command -v cp)
cat > "$scratch/bin/cp" <<'WRAPPER'
#!/bin/sh
set -eu
"$REAL_CP" "$@"
for destination do :; done
if test "$destination" = "$CORRUPT_DEST"; then
    printf X | dd of="$destination" bs=1 seek=0 conv=notrunc 2>/dev/null
fi
WRAPPER
chmod +x "$scratch/bin/cp"
# A failed rebuild must preserve the prior final stage and manifest.
if env PATH="$scratch/bin:$PATH" REAL_CP="$real_cp" CORRUPT_DEST="$root/distfiles/hello-local.txt" \
    make -s -j8 -f mk/pkg.mk ROOT="$root" package > "$scratch/corruption.log" 2>&1; then
    fail 'same-size copied-source corruption passed'
fi
grep 'source-hash-mismatch' "$scratch/corruption.log" >/dev/null || fail 'wrong corruption failure'
cmp "$scratch/payload" "$root/stage/hello-local/usr/local/share/hello-local/hello.txt"
cmp "$scratch/serial.manifest" "$root/manifests/hello-local.manifest"
# On a fresh root, neither extraction nor final outputs may appear.
new_root corrupt
if env PATH="$scratch/bin:$PATH" REAL_CP="$real_cp" CORRUPT_DEST="$root/distfiles/hello-local.txt" \
    make -s -j8 -f mk/pkg.mk ROOT="$root" package > "$scratch/corruption.log" 2>&1; then
    fail 'fresh corrupted build passed'
fi
grep -qx verify-failure "$root/logs/hello-local/phase.log"
! grep -q extract-start "$root/logs/hello-local/phase.log" || fail 'extracted corrupt bytes'
test ! -e "$root/work/hello-local/hello.txt"
test ! -e "$root/manifests/hello-local.manifest"

# A failed publication tool must leave the prior path manifest intact.
new_root publication
pm package > /dev/null
cp "$root/manifests/hello-local.manifest" "$scratch/prior.manifest"
printf extra > "$root/stage/hello-local/extra.txt"
printf '#!/bin/sh\nexit 1\n' > "$scratch/bin/cut"
chmod +x "$scratch/bin/cut"
if env PATH="$scratch/bin:$PATH" REAL_CP="$real_cp" CORRUPT_DEST=unused \
    make -s -f mk/pkg.mk ROOT="$root" manifest > "$scratch/publication.log" 2>&1; then
    fail 'failed manifest tool passed'
fi
cmp "$scratch/prior.manifest" "$root/manifests/hello-local.manifest"
grep -qx manifest-failure "$root/logs/hello-local/phase.log"
test -z "$(find "$root/manifests" -name '*.tmp.*' -print)" || fail 'temporary manifest leaked'

# Reject unsafe parameters before logging, copying, or cleanup.
new_root guarded
for assignment in ROOT= ROOT=/ ROOT="$HOME" ROOT="$PWD" ROOT="$scratch/missing" \
    ROOT="$root/../guarded" DESTDIR=/ STAGEDIR="$scratch" WRKDIR="$scratch" \
    DISTDIR="$scratch" DISTFILE="$scratch/out" LOGDIR="$scratch" MANIFEST="$scratch/out" \
    PREFIX=/../escape PREFIX=relative PKGNAME=../escape
do
    reject "$assignment" package
    reject "$assignment" clean
done
test -z "$(find "$root" ! -path "$root" ! -name .pkg-mgr-root -print)" || fail 'rejection mutated root'
chmod 0755 "$root"
reject package
chmod 0700 "$root"
ln -s "$root" "$scratch/root-link"
reject ROOT="$scratch/root-link" package
reject ROOT="$scratch/root-link/" package
new_root uninitialized
rm "$root/.pkg-mgr-root"
reject package
printf preserve > "$root/sentinel"
reject init-root
test "$(cat "$root/sentinel")" = preserve

# Existing links at any depth must block builds and cleanup, preserving outsiders.
new_root linked
mkdir "$scratch/outside"
printf preserve > "$scratch/outside/sentinel"
ln -s "$scratch/outside" "$root/work"
reject package
reject clean
test "$(cat "$scratch/outside/sentinel")" = preserve
rm "$root/work"
ln -s "$scratch/missing" "$root/dangling"
reject package
rm "$root/dangling"
ln "$scratch/outside/sentinel" "$root/hardlink"
reject package
reject clean
rm "$root/hardlink"
mkfifo "$root/fifo"
reject package
reject clean
rm "$root/fifo"
pm package > /dev/null
printf '%s\n' 'Package ordering, copied-source integrity, publication failure, and private-root checks passed'
