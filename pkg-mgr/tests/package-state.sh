#!/bin/sh
set -eu
repo=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
cd "$repo"
scratch=$(mktemp -d "$repo/.pkg-mgr-state-test.XXXXXX")
trap 'rm -rf "$scratch"' 0
trap 'exit 1' HUP INT TERM
root=$scratch/'private root'
(umask 077; mkdir "$root")
state() { action=$1; shift; sh mk/state.sh "$action" "$root" "$@"; }
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }
reject() {
    if "$@" > "$scratch/reject.out" 2> "$scratch/reject.err"; then fail 'invalid operation succeeded'; fi
    test ! -s "$scratch/reject.out" || fail 'invalid state emitted a partial view'
}
hash() { sh mk/verify-metadata.sh hash-file "$1"; }
# Build evidence uses the existing generator and repository-relative references.
make_evidence() {
    name=$1
    mkdir -p "$root/stage/$name/usr/local/share/$name" "$scratch/evidence/$name"
    cp fixtures/sources/hello-local/hello.txt "$root/stage/$name/usr/local/share/$name/payload.txt"
    manifest=$scratch/evidence/$name/manifest.tsv
    build=$scratch/evidence/$name/build.kv
    deps=$scratch/evidence/$name/deps
    : > "$deps"
    if test "$name" = base; then
        cp fixtures/sources/hello-local/hello.txt "$root/stage/$name/usr/local/share/$name/file with spaces.txt"
    fi
    sh mk/verify-metadata.sh manifest "$root/stage/$name" "$manifest" > /dev/null
    manifest_ref=${manifest#"$repo/"}
    # Use ENVIRON so backslashes in a host path never become awk escapes.
    NAME=$name MANIFEST_REF=$manifest_ref awk '
      /^package_name=/ {print "package_name=" ENVIRON["NAME"]; next}
      /^manifest_ref=/ {print "manifest_ref=" ENVIRON["MANIFEST_REF"]; next}
      {print}' fixtures/metadata-boundary/build-input.kv > "$scratch/evidence/$name/input.kv"
    sh mk/verify-metadata.sh build-record "$scratch/evidence/$name/input.kv" "$build" > /dev/null 2>&1
}
register() { state register "$scratch/evidence/$1/manifest.tsv" "$scratch/evidence/$1/build.kv" "$scratch/evidence/$1/deps"; }
make -s -f mk/pkg.mk ROOT="$root" init-root
state init > /dev/null
state list > "$scratch/list"
test ! -s "$scratch/list"
reject state init
for name in base app spare; do make_evidence "$name"; done
printf 'base\n' > "$scratch/evidence/app/deps"
reject register app # missing dependency, nothing published
state check-register "$scratch/evidence/base/manifest.tsv" "$scratch/evidence/base/build.kv" "$scratch/evidence/base/deps" > /dev/null
test ! -e "$root/state/packages/base.tsv"
register base > /dev/null
register app > /dev/null
register spare > /dev/null
printf '# requested packages\napp\n' > "$root/state/world"
state list > "$scratch/list"
printf 'app\t0.1\texplicit\nbase\t0.1\tdependency\nspare\t0.1\tdependency\n' > "$scratch/expected"
cmp "$scratch/list" "$scratch/expected"
test "$(state deps app)" = base
test "$(state rdeps base)" = app
state owners > "$scratch/owners"
grep 'usr/local/share/base/payload.txt' "$scratch/owners" > /dev/null
state files app > "$scratch/files"
grep '^usr/local/share/app/payload.txt' "$scratch/files" > /dev/null
reject state files missing
state orphans > "$scratch/orphans"
printf 'report\torphan-plan-v1\tnon-deleting\norphan\tspare\n' > "$scratch/expected"
cmp "$scratch/orphans" "$scratch/expected"
state verify > "$scratch/verified"
grep '^verified' "$scratch/verified" > /dev/null

python3 tests/cli-populated.py "$root"

# Re-registration and all read-only views preserve every authoritative byte.
cp "$root/state/packages/app.tsv" "$scratch/prior.app"
register app > "$scratch/reregister"
grep '^already-registered' "$scratch/reregister" > /dev/null
cmp "$scratch/prior.app" "$root/state/packages/app.tsv"
find "$root" -type f -exec sh -c 'verifier=$1; shift; for p do sh "$verifier" hash-file "$p"; done' sh "$repo/mk/verify-metadata.sh" {} + > "$scratch/before.hashes"
for command in list owners orphans verify; do state "$command" > /dev/null; done
find "$root" -type f -exec sh -c 'verifier=$1; shift; for p do sh "$verifier" hash-file "$p"; done' sh "$repo/mk/verify-metadata.sh" {} + > "$scratch/after.hashes"
cmp "$scratch/before.hashes" "$scratch/after.hashes"
# World order has no effect; malformed or unknown roots produce no report.
printf 'spare\napp\n' > "$root/state/world"
state orphans > "$scratch/order-one"
printf 'app\nspare\n' > "$root/state/world"
state orphans > "$scratch/order-two"
cmp "$scratch/order-one" "$scratch/order-two"
printf 'app\napp\n' > "$root/state/world"
reject state orphans
printf 'unknown\n' > "$root/state/world"
reject state orphans
printf 'app\n' > "$root/state/world"

# Same path owned by another package is refused before publication.
make_evidence conflict
mkdir -p "$root/stage/conflict/usr/local/share/app"
cp fixtures/sources/hello-local/hello.txt "$root/stage/conflict/usr/local/share/app/payload.txt"
sh mk/verify-metadata.sh manifest "$root/stage/conflict" "$scratch/evidence/conflict/manifest.tsv" >/dev/null
sh mk/verify-metadata.sh build-record "$scratch/evidence/conflict/input.kv" "$scratch/evidence/conflict/build.kv" >/dev/null 2>&1
reject register conflict
grep 'state-conflict' "$scratch/reject.err" > /dev/null
test ! -e "$root/state/packages/conflict.tsv"

# Permission-only changes are observable without changing content or size.
mode_path=$root/stage/app/usr/local/share/app/payload.txt
original_mode=$(sh mk/file-mode.sh "$mode_path")
chmod 0755 "$mode_path"
if state verify > "$scratch/mode-report"; then fail 'changed permissions verified'; fi
grep '^mode-mismatch' "$scratch/mode-report" >/dev/null
reject register app
cmp "$scratch/prior.app" "$root/state/packages/app.tsv"
chmod "$original_mode" "$mode_path"
# Legacy records remain inspectable; missing permission evidence fails verification.
awk -F '\t' 'BEGIN{OFS="\t"} NR==1 {print "format", "pkg-state-v1"; next} $1=="file" {print $1,$2,$3,$4; next} {print}' "$scratch/prior.app" > "$root/state/packages/app.tsv"
state files app > "$scratch/legacy-files"
grep 'untracked$' "$scratch/legacy-files" >/dev/null
if state verify > "$scratch/legacy-report"; then fail 'legacy modes silently verified'; fi
grep '^mode-untracked' "$scratch/legacy-report" >/dev/null
reject register app
cp "$scratch/prior.app" "$root/state/packages/app.tsv"
state verify >/dev/null

# Tampered payload, missing file, directory substitution, extra file, and symlink.
payload=$root/stage/app/usr/local/share/app/payload.txt
cp "$payload" "$scratch/payload"
printf X | dd of="$payload" bs=1 seek=0 conv=notrunc 2>/dev/null
if state verify > "$scratch/report"; then fail 'changed payload verified'; fi
grep '^content-mismatch' "$scratch/report" > /dev/null
reject register app
cmp "$scratch/prior.app" "$root/state/packages/app.tsv"
rm "$payload"
if state verify > "$scratch/report"; then fail 'missing payload verified'; fi
grep '^missing' "$scratch/report" > /dev/null
mkdir "$payload"
if state verify > "$scratch/report"; then fail 'directory verified as file'; fi
grep '^type-mismatch' "$scratch/report" > /dev/null
rmdir "$payload"
cp "$scratch/payload" "$payload"
printf extra >> "$payload"
if state verify > "$scratch/report"; then fail 'wrong-size file verified'; fi
grep '^size-mismatch' "$scratch/report" > /dev/null
cp "$scratch/payload" "$payload"
printf extra > "$root/stage/app/extra.txt"
if state verify > "$scratch/report"; then fail 'unowned file verified'; fi
grep '^unowned' "$scratch/report" > /dev/null
rm "$root/stage/app/extra.txt"
ln -s "$scratch/payload" "$root/stage/app/link"
if state verify > "$scratch/report"; then fail 'symlink verified'; fi
grep '^unsupported-type' "$scratch/report" > /dev/null
reject register app
rm "$root/stage/app/link"

# Authoritative schema/hash failures cannot produce inspection or candidate output.
for mutation in duplicate traversal unknown fingerprint mode; do
    cp "$scratch/prior.app" "$root/state/packages/app.tsv"
    case $mutation in
      duplicate) tail -n 1 "$scratch/prior.app" >> "$root/state/packages/app.tsv" ;;
      traversal) sed 's@usr/local/share/app/payload.txt@../escape@' "$scratch/prior.app" > "$root/state/packages/app.tsv" ;;
      mode) awk -F '\t' 'BEGIN{OFS="\t"} $1=="file" {$5="4755"} {print}' "$scratch/prior.app" > "$root/state/packages/app.tsv" ;;
      unknown) printf 'unknown\tdata\n' >> "$root/state/packages/app.tsv" ;;
      fingerprint) sed 's@usr/local/share/app/payload.txt@usr/local/share/app/changed.txt@' "$scratch/prior.app" > "$root/state/packages/app.tsv" ;;
    esac
    reject state list
    reject state orphans
done
cp "$scratch/prior.app" "$root/state/packages/app.tsv"
# A validly formatted dangling dependency must block every derived view.
awk '$0 ~ /^file\t/ && !inserted {print "dependency\tmissing"; inserted=1} {print}' "$scratch/prior.app" > "$root/state/packages/app.tsv"
reject state orphans
grep 'state-dangling' "$scratch/reject.err" >/dev/null
cp "$scratch/prior.app" "$root/state/packages/app.tsv"
# Evidence values remain inert even when they contain shell syntax.
make_evidence inert
sed "s/^builder_label=.*/builder_label=\$(touch SHOULD-NOT-EXIST)/" "$scratch/evidence/inert/build.kv" > "$scratch/inert.build"
mv "$scratch/inert.build" "$scratch/evidence/inert/build.kv"
register inert > /dev/null
test ! -e SHOULD-NOT-EXIST
# Remove this test record only in the test harness to restore the three-node graph.
rm "$root/state/packages/inert.tsv"
# Dependency cycles terminate and follow world closure; no pruning or deletion.
cp "$root/state/packages/base.tsv" "$scratch/prior.base"
awk '$0 ~ /^file\t/ && !inserted {print "dependency\tapp"; inserted=1} {print}' "$scratch/prior.base" > "$root/state/packages/base.tsv"
state orphans > "$scratch/cycle"
grep '^orphan.*spare$' "$scratch/cycle" > /dev/null
: > "$root/state/world"
state orphans > "$scratch/cycle-unrooted"
test "$(grep -c '^orphan' "$scratch/cycle-unrooted")" -eq 3
cp "$scratch/prior.base" "$root/state/packages/base.tsv"
printf 'app\n' > "$root/state/world"

# Publication failure leaves the record set and prior bytes unchanged.
make_evidence pending
mkdir "$scratch/bin"
printf '#!/bin/sh\nexit 1\n' > "$scratch/bin/mv"
chmod +x "$scratch/bin/mv"
reject env PATH="$scratch/bin:$PATH" sh mk/state.sh register "$root" "$scratch/evidence/pending/manifest.tsv" "$scratch/evidence/pending/build.kv" "$scratch/evidence/pending/deps"
test ! -e "$root/state/packages/pending.tsv"
test -z "$(find "$root/state/packages" -name '.pending.*' -print)"
cmp "$scratch/prior.app" "$root/state/packages/app.tsv"
state verify > /dev/null
# Registered stages cannot be silently rebuilt or removed by the old build driver.
make -s -f mk/pkg.mk ROOT="$root" package > /dev/null
make_evidence hello-local
register hello-local > /dev/null
reject make -s -f mk/pkg.mk ROOT="$root" package
reject make -s -f mk/pkg.mk ROOT="$root" clean
state verify > /dev/null
printf 'Package records, world roots, derived views, verification, and non-deleting orphan checks passed\n'
