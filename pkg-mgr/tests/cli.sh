#!/bin/sh
set -eu
repo=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
scratch=$(mktemp -d "${TMPDIR:-/tmp}/pkg-cli-test.XXXXXX")
trap 'rm -rf "$scratch"' 0
trap 'exit 1' HUP INT TERM
cli=$repo/bin/pkg-mgr
reject64() {
    code=0
    "$cli" "$@" > "$scratch/out" 2> "$scratch/err" || code=$?
    test "$code" -eq 64
}
"$cli" --help > "$scratch/help" 2> "$scratch/err"
test ! -s "$scratch/err"
grep 'private-root' "$scratch/help" >/dev/null
"$cli" --version | grep '^pkg-mgr 0.1.0' >/dev/null
reject64
reject64 --root /tmp --plain --color=always list
reject64 --root /tmp --format=tsv --color=always list
reject64 --root /tmp --color=never --color=always list
reject64 --root /tmp --progress=always list
reject64 --root /tmp remove app
reject64 --root "$(printf '/tmp/root\033[2J')" list
root=$scratch/'private root'
mkdir -m 700 "$root"
make -s -f "$repo/mk/pkg.mk" ROOT="$root" init-root
sh "$repo/mk/state.sh" init "$root" >/dev/null
# stdout in machine mode is exactly the existing command protocol.
for action in list owners verify orphans; do
    sh "$repo/mk/state.sh" "$action" "$root" > "$scratch/expected"
    "$cli" --root="$root" --format=tsv "$action" > "$scratch/out" 2> "$scratch/err"
    cmp "$scratch/expected" "$scratch/out"
    test ! -s "$scratch/err"
done
"$cli" --root "$root" --plain verify > "$scratch/out" 2> "$scratch/err"
grep '^Verified staged file contents' "$scratch/out" >/dev/null
test ! -s "$scratch/err"
# Explicit color works without a TTY; auto never emits ANSI to redirected stderr.
for color in auto never always; do
    code=0
    TERM=xterm NO_COLOR=1 "$cli" --root "$scratch/missing" --color "$color" list > "$scratch/out" 2> "$scratch/err" || code=$?
    test "$code" -eq 1
    esc=$(printf '\033')
    if test "$color" = always; then grep "$esc" "$scratch/err" >/dev/null
    elif grep "$esc" "$scratch/err"; then exit 1
    fi
done
# Escape controls in human diagnostics; never let helper text control the terminal.
printf 'bad\033[31m\rname\n' | awk -v diagnostic=yes -f "$repo/mk/cli-render.awk" > "$scratch/escaped"
grep -F '\x1b[31m\x0dname' "$scratch/escaped" >/dev/null
# Plain presentation also escapes non-ASCII bytes deterministically.
printf '\303\251\n' | LC_ALL=C awk -v plain=yes -v diagnostic=yes -f "$repo/mk/cli-render.awk" > "$scratch/escaped"
grep -F '\xc3\xa9' "$scratch/escaped" >/dev/null
# Preserve helpers' failure status and byte streams in machine mode.
code=0
sh "$repo/mk/state.sh" list "$scratch/missing" > "$scratch/expected" 2> "$scratch/expected-err" || code=$?
actual=0
"$cli" --root "$scratch/missing" --format tsv list > "$scratch/out" 2> "$scratch/err" || actual=$?
test "$actual" -eq "$code"
cmp "$scratch/expected" "$scratch/out"
cmp "$scratch/expected-err" "$scratch/err"
mkdir "$root/.replacement"
code=0
"$cli" --root "$root" verify > "$scratch/out" 2> "$scratch/err" || code=$?
test "$code" -eq 1
grep 'replacement pending' "$scratch/err" >/dev/null
printf 'CLI help/options, streams, modes, escaping, exit status and pending guard passed\n'
