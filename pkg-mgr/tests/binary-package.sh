#!/bin/sh
# Synthetic host receipts keep ordinary transport tests compiler/network-free.
set -eu
repo=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
cd "$repo"
scratch=$(mktemp -d "$repo/.pkg-mgr-binary-test.XXXXXX")
trap 'rm -rf "$scratch"' 0
trap 'exit 1' HUP INT TERM
hash() { sh mk/verify-metadata.sh hash-file "$1"; }
init() { mkdir -m 700 "$1"; make -s -f mk/pkg.mk ROOT="$1" init-root; sh mk/state.sh init "$1" >/dev/null; }
reject() { if "$@" > "$scratch/out" 2> "$scratch/err"; then printf 'FAIL: accepted invalid binary operation\n' >&2; exit 1; fi; }
snapshot() {
    find "${1:-$fresh}" -type f -exec sh -c '
        for path do
            printf "%s\t%s\t%s\n" "$path" "$(sh mk/verify-metadata.sh hash-file "$path")" "$(sh mk/file-mode.sh "$path")"
        done' sh {} + | sort
}
reader_tools=$scratch/reader-tools
mkdir "$reader_tools"
reader_awk=$(command -v awk); reader_uname=$(command -v uname); reader_sed=$(command -v sed)
cat > "$reader_tools/awk" <<'READER_TOOL'
#!/bin/sh
selected=no
case ${0##*/} in
    awk)
        real=$READER_AWK
        if test "$READER_KIND" = field && test "$#" -eq 2 && test "${KEY-}" = "$READER_KEY"; then
            case $2 in */host.kv) selected=yes;; esac
        fi ;;
    uname)
        real=$READER_UNAME
        if test "$READER_KIND" = uname && test "$#" -eq 1 && test "$1" = "$READER_KEY"; then selected=yes; fi ;;
    sed)
        real=$READER_SED
        if test "$READER_KIND" = version && test "$#" -eq 3 && test "$1" = -n && test "$2" = 1p; then
            case $3 in */package.tsv) selected=yes;; esac
        fi ;;
esac
if test "$selected" = yes; then
    "$real" "$@" || exit
    printf 'injected-binary-reader-error\n' >&2
    exit 73
fi
exec "$real" "$@"
READER_TOOL
cp "$reader_tools/awk" "$reader_tools/uname"
cp "$reader_tools/awk" "$reader_tools/sed"
chmod +x "$reader_tools/awk" "$reader_tools/uname" "$reader_tools/sed"
reader_reject() {
    reader_kind=$1; reader_key=$2; shift 2
    reject env PATH="$reader_tools:$PATH" READER_AWK="$reader_awk" READER_UNAME="$reader_uname" READER_SED="$reader_sed" \
        READER_KIND="$reader_kind" READER_KEY="$reader_key" "$@"
    grep '^injected-binary-reader-error$' "$scratch/err" >/dev/null
    test ! -s "$scratch/out"
}
source_root=$scratch/source
fresh=$scratch/fresh
init "$source_root"
init "$fresh"
for name in base app; do
    stage=$source_root/stage/$name
    mkdir -p "$stage/usr/local/share/pkg-mgr/$name" "$scratch/$name"
    printf '#!/bin/sh\nprintf transported\\n\n' > "$stage/$name"
    chmod 0755 "$stage/$name"
    if test "$name" = app; then printf old > "$stage/obsolete"; fi
    host=$stage/usr/local/share/pkg-mgr/$name/host.kv
    printf 'host_os=%s\nhost_arch=%s\ncompiler_target=test-host-v1\ntarget_runtime=host-only\n' "$(uname -s)" "$(uname -m)" > "$host"
    chmod 0600 "$host"
    : > "$scratch/$name/deps"
    if test "$name" = app; then
        printf 'base\n' > "$scratch/$name/deps"
        printf 'dependency_base_record_sha256=%s\n' "$(hash "$source_root/state/packages/base.tsv")" >> "$host"
    fi
    manifest=$scratch/$name/manifest.tsv
    sh mk/verify-metadata.sh manifest "$stage" "$manifest" >/dev/null
    NAME=$name REF=${manifest#"$repo/"} awk '
      /^package_name=/ {print "package_name=" ENVIRON["NAME"]; next}
      /^manifest_ref=/ {print "manifest_ref=" ENVIRON["REF"]; next}
      {print}' fixtures/metadata-boundary/build-input.kv > "$scratch/$name/input.kv"
    sh mk/verify-metadata.sh build-record "$scratch/$name/input.kv" "$scratch/$name/build.kv" >/dev/null 2>&1
    sh mk/state.sh register "$source_root" "$manifest" "$scratch/$name/build.kv" "$scratch/$name/deps" >/dev/null
    if test "$name" = base; then
        descriptor_tools=$scratch/descriptor-tools
        mkdir "$descriptor_tools"
        descriptor_sh=$(command -v sh)
        cat > "$descriptor_tools/sh" <<'DESCRIPTOR_TOOL'
#!/bin/sh
if test "$#" -eq 3 && test "${1##*/}" = verify-metadata.sh && test "$2" = hash-file; then
    case $3 in
        */.binary-work.*/bundle/"$DESCRIPTOR_FIELD"|"${DESCRIPTOR_BUNDLE:-/unused}/$DESCRIPTOR_FIELD")
            printf 'injected-descriptor-hash-error\n' >&2
            exit 73 ;;
    esac
fi
exec "$DESCRIPTOR_SH" "$@"
DESCRIPTOR_TOOL
        chmod +x "$descriptor_tools/sh"
        snapshot "$source_root" > "$scratch/before-descriptor"
        for descriptor_field in package.tsv target.kv modes.tsv dependencies.tsv artifact.kv; do
            reject env PATH="$descriptor_tools:$PATH" DESCRIPTOR_SH="$descriptor_sh" DESCRIPTOR_FIELD="$descriptor_field" DESCRIPTOR_BUNDLE="$source_root/binaries/base" \
                sh mk/binary.sh export "$source_root" base
            grep '^injected-descriptor-hash-error$' "$scratch/err" >/dev/null
            test ! -s "$scratch/out"
            test ! -e "$source_root/binaries/base"
            snapshot "$source_root" > "$scratch/after-descriptor"
            cmp "$scratch/before-descriptor" "$scratch/after-descriptor"
        done
    fi
    if test "$name" = app; then
        snapshot "$source_root" > "$scratch/before-reader-export"
        for reader_key in target_runtime dependency_base_record_sha256 host_os host_arch compiler_target; do
            reader_reject field "$reader_key" sh mk/binary.sh export "$source_root" app
            test ! -e "$source_root/binaries/app"
            snapshot "$source_root" > "$scratch/after-reader-export"
            cmp "$scratch/before-reader-export" "$scratch/after-reader-export"
        done
    fi
    # Exercise the public CLI with real exported package artifacts.
    bin/pkg-mgr --root "$source_root" --format tsv export "$name" > "$scratch/exported" 2> "$scratch/cli.err"
    test ! -s "$scratch/cli.err"
    printf 'exported\t%s\t%s\n' "$name" "$(hash "$source_root/binaries/$name/artifact.kv")" > "$scratch/expected-export"
    cmp "$scratch/expected-export" "$scratch/exported"
    reject sh mk/binary.sh export "$source_root" "$name"
done
base=$source_root/binaries/base
app=$source_root/binaries/app
base_pin=$(hash "$base/artifact.kv")
app_pin=$(hash "$app/artifact.kv")
snapshot "$fresh" > "$scratch/before-descriptor-import"
for descriptor_field in package.tsv target.kv modes.tsv dependencies.tsv; do
    reject env PATH="$descriptor_tools:$PATH" DESCRIPTOR_SH="$descriptor_sh" DESCRIPTOR_FIELD="$descriptor_field" DESCRIPTOR_BUNDLE="$base" \
        sh mk/binary.sh import "$fresh" "$base" "$base_pin" test-host-v1
    grep '^injected-descriptor-hash-error$' "$scratch/err" >/dev/null
    test ! -s "$scratch/out"
    test ! -e "$fresh/stage/base"
    test ! -e "$fresh/state/packages/base.tsv"
    snapshot "$fresh" > "$scratch/after-descriptor-import"
    cmp "$scratch/before-descriptor-import" "$scratch/after-descriptor-import"
done
printf 'Nine binary descriptor hash failures reject before publication or receipts\n'
import() { bin/pkg-mgr --root "$fresh" --format tsv import "$1" "$2" test-host-v1; }
reject import "$app" "$app_pin" # dependency absent
reject sh mk/binary.sh import "$fresh" "$base" "$base_pin" wrong-target
reject import "$base" "$app_pin"
# Mutations with newly pinned outer descriptors exercise inner validation too.
rebind() {
    for pair in 'record package.tsv' 'target target.kv' 'modes modes.tsv' 'dependencies dependencies.tsv'; do
        set -- "${pair%% *}" "${pair#* }"
        KEY=${1}_sha256 VALUE=$(hash "$bad/$2") awk -F= '$1==ENVIRON["KEY"] {print $1 "=" ENVIRON["VALUE"]; next} {print}' "$bad/artifact.kv" > "$scratch/descriptor"
        mv "$scratch/descriptor" "$bad/artifact.kv"
    done
}
for mutation in blob mode traversal extra symlink hardlink target dependency; do
    bad=$scratch/bad
    cp -R "$base" "$bad"
    case $mutation in
        blob) blob=$(awk -F '\t' '$1=="file"{print $2; exit}' "$bad/package.tsv"); printf corrupt > "$bad/files/$blob" ;;
        mode) sed 's/0755/4755/' "$bad/modes.tsv" > "$scratch/modes"; mv "$scratch/modes" "$bad/modes.tsv"; rebind ;;
        traversal) awk -F '\t' 'BEGIN{OFS="\t"} $1=="file" && $4=="base" {$4="../escape"} {print}' "$bad/package.tsv" > "$scratch/record"; mv "$scratch/record" "$bad/package.tsv"; rebind ;;
        extra) touch "$bad/unknown" ;;
        symlink) ln -s "$base/package.tsv" "$bad/link" ;;
        hardlink) ln "$bad/package.tsv" "$scratch/linked" ;;
        target) sed 's/test-host-v1/wrong-target/' "$bad/target.kv" > "$scratch/target"; mv "$scratch/target" "$bad/target.kv"; rebind ;;
        dependency) printf 'unknown\t%s\n' "$base_pin" > "$bad/dependencies.tsv"; rebind ;;
    esac
    reject import "$bad" "$(hash "$bad/artifact.kv")"
    test ! -e "$fresh/stage/base"
    test ! -e "$fresh/state/packages/base.tsv"
    rm -rf "$bad"
    rm -f "$scratch/linked"
done
import "$base" "$base_pin" > "$scratch/imported" 2> "$scratch/cli.err"
printf 'imported\tbase\n' > "$scratch/expected-import"
cmp "$scratch/expected-import" "$scratch/imported"
test ! -s "$scratch/cli.err"
cmp "$base/package.tsv" "$fresh/state/packages/base.tsv"
test -x "$fresh/stage/base/base"
snapshot "$fresh" > "$scratch/before-reader-import"
for reader_key in target_runtime dependency_base_record_sha256 host_os host_arch compiler_target uname-s uname-m version; do
    case $reader_key in
        uname-s) reader_kind='uname'; reader_key=-s ;;
        uname-m) reader_kind='uname'; reader_key=-m ;;
        version) reader_kind=version ;;
        *) reader_kind=field ;;
    esac
    reader_reject "$reader_kind" "$reader_key" sh mk/binary.sh import "$fresh" "$app" "$app_pin" test-host-v1
    test ! -e "$fresh/stage/app"
    test ! -e "$fresh/state/packages/app.tsv"
    snapshot "$fresh" > "$scratch/after-reader-import"
    cmp "$scratch/before-reader-import" "$scratch/after-reader-import"
done
printf 'Thirteen binary reader failures reject plausible output before publication\n'

test "$(sh mk/file-mode.sh "$fresh/stage/base/usr/local/share/pkg-mgr/base/host.kv")" = 0600
printf 'base\n' > "$fresh/state/world"
cp "$fresh/state/world" "$scratch/world"
# Simulate failure after payload publication, before the authoritative record.
mkdir "$scratch/bin"
real_mv=$(command -v mv)
cat > "$scratch/bin/mv" <<'WRAPPER'
#!/bin/sh
for arg do test "$arg" != "$FAIL_DEST" || exit 1; done
exec "$REAL_MV" "$@"
WRAPPER
chmod 0755 "$scratch/bin/mv"
reject env PATH="$scratch/bin:$PATH" REAL_MV="$real_mv" FAIL_DEST="$fresh/state/packages/app.tsv" sh mk/binary.sh import "$fresh" "$app" "$app_pin" test-host-v1
test ! -e "$fresh/stage/app"
test ! -e "$fresh/state/packages/app.tsv"
cmp "$base/package.tsv" "$fresh/state/packages/base.tsv"
sh mk/state.sh verify "$fresh" >/dev/null
import "$app" "$app_pin" > "$scratch/imported" 2> "$scratch/cli.err"
printf 'imported\tapp\n' > "$scratch/expected-import"
cmp "$scratch/expected-import" "$scratch/imported"
test ! -s "$scratch/cli.err"
reject import "$app" "$app_pin"
cmp "$app/package.tsv" "$fresh/state/packages/app.tsv"
cmp "$scratch/world" "$fresh/state/world"
sh mk/state.sh verify "$fresh" >/dev/null
test -z "$(find "$fresh" -name '.binary-work.*' -print)"
printf 'Binary round trips, target/integrity rejection, modes and failed-publication preservation passed\n'

# A killed importer cannot run its cleanup trap. Exercise both publication gaps.
recovery=$scratch/recovery
init "$recovery"
sh mk/binary.sh import "$recovery" "$base" "$base_pin" test-host-v1 >/dev/null
recover() { bin/pkg-mgr --root "$recovery" --format tsv recover "$app" "$app_pin" test-host-v1; }
reject recover # no stage to adopt
cat > "$scratch/bin/mv" <<'WRAPPER'
#!/bin/sh
for arg do
    if test "$arg" = "$FAIL_DEST"; then
        if test "$KILL_AFTER" = yes; then "$REAL_MV" "$@" || exit; fi
        kill -KILL "$PPID"
        exit 1
    fi
done
exec "$REAL_MV" "$@"
WRAPPER
reject env PATH="$scratch/bin:$PATH" REAL_MV="$real_mv" FAIL_DEST="$recovery/state/packages/app.tsv" KILL_AFTER=no sh mk/binary.sh import "$recovery" "$app" "$app_pin" test-host-v1
test -f "$recovery/stage/app/app"
test ! -e "$recovery/state/packages/app.tsv"
# CLI recovery adopts a copied interrupted stage; original fault path stays pending.
cli_recovery=$scratch/cli-recovery
cp -Rp "$recovery" "$cli_recovery"
cp "$cli_recovery/state/world" "$scratch/cli-world"
for retry in first second; do
    bin/pkg-mgr --root "$cli_recovery" --format tsv recover "$app" "$app_pin" test-host-v1 > "$scratch/recovered" 2> "$scratch/cli.err"
    printf 'recovered\tapp\n' > "$scratch/expected-recovery"
    cmp "$scratch/expected-recovery" "$scratch/recovered"
    test ! -s "$scratch/cli.err"
    cmp "$base/package.tsv" "$cli_recovery/state/packages/base.tsv"
    cmp "$app/package.tsv" "$cli_recovery/state/packages/app.tsv"
    cmp "$scratch/cli-world" "$cli_recovery/state/world"
    sh mk/state.sh verify "$cli_recovery" >/dev/null
    snapshot "$cli_recovery" > "$scratch/cli-$retry"
done
cmp "$scratch/cli-first" "$scratch/cli-second"
printf 'CLI export/import and retained-stage recovery receipts passed\n'
# Every rejected recovery preserves the interrupted payload as found.
chmod 0644 "$recovery/stage/app/app"
reject recover
test -f "$recovery/stage/app/app"
test ! -e "$recovery/state/packages/app.tsv"
chmod 0755 "$recovery/stage/app/app"
printf changed >> "$recovery/stage/app/app"
reject recover
grep changed "$recovery/stage/app/app" >/dev/null
cp "$source_root/stage/app/app" "$recovery/stage/app/app"
printf extra > "$recovery/stage/app/extra"
reject recover
test -f "$recovery/stage/app/extra"
rm "$recovery/stage/app/extra"
ln -s app "$recovery/stage/app/link"
reject recover
test -L "$recovery/stage/app/link"
rm "$recovery/stage/app/link"
# Kill recovery after its single record rename: retry must be idempotent.
reject env PATH="$scratch/bin:$PATH" REAL_MV="$real_mv" FAIL_DEST="$recovery/state/packages/app.tsv" KILL_AFTER=yes sh mk/binary.sh recover "$recovery" "$app" "$app_pin" test-host-v1
cmp "$app/package.tsv" "$recovery/state/packages/app.tsv"
recover >/dev/null
recover >/dev/null
cmp "$base/package.tsv" "$recovery/state/packages/base.tsv"
cmp "$app/package.tsv" "$recovery/state/packages/app.tsv"
sh mk/state.sh verify "$recovery" >/dev/null
# A committed package with changed executable permissions is also rejected.
chmod 0775 "$recovery/stage/app/app"
reject recover
cmp "$app/package.tsv" "$recovery/state/packages/app.tsv"
printf 'Killed import/recovery, mismatch preservation and idempotent recovery passed\n'

# A real second fixture package version: changed bytes/mode and a new file.
updated=$scratch/updated
cp -Rp "$source_root" "$updated"
rm -rf "$updated/binaries"
rm "$updated/state/packages/app.tsv"
printf '\n# version 0.2\n' >> "$updated/stage/app/app"
chmod 0700 "$updated/stage/app/app"
rm "$updated/stage/app/obsolete"
printf 'default=yes\n' > "$updated/stage/app/new.conf"
sh mk/verify-metadata.sh manifest "$updated/stage/app" "$scratch/app/manifest.tsv" >/dev/null
sed 's/^version=.*/version=0.2/' "$scratch/app/input.kv" > "$scratch/app/input2.kv"
sh mk/verify-metadata.sh build-record "$scratch/app/input2.kv" "$scratch/app/build2.kv" >/dev/null 2>&1
sh mk/state.sh register "$updated" "$scratch/app/manifest.tsv" "$scratch/app/build2.kv" "$scratch/app/deps" >/dev/null
sh mk/binary.sh export "$updated" app >/dev/null
next=$updated/binaries/app
next_pin=$(hash "$next/artifact.kv")
preflight() { bin/pkg-mgr --format tsv --root "$fresh" preflight "$next" "$next_pin" test-host-v1; }
# Final report pins must succeed before even the report header is emitted.
report_tools=$scratch/report-tools
mkdir "$report_tools"
report_sh=$(command -v sh)
cat > "$report_tools/sh" <<'REPORT_TOOL'
#!/bin/sh
if test "$#" -eq 3 && test "${1##*/}" = verify-metadata.sh && test "$2" = hash-file && test "$3" = "$REPORT_FILE"; then
    count=0
    if test -f "$REPORT_COUNT"; then read -r count < "$REPORT_COUNT"; fi
    count=$((count + 1))
    printf '%s\n' "$count" > "$REPORT_COUNT"
    if test "$count" -eq "$REPORT_FAIL_AT"; then
        printf 'injected-preflight-receipt-hash-error\n' >&2
        if test "$REPORT_OUTPUT" = digest; then "$REPORT_SH" "$@" || exit; fi
        exit 73
    fi
fi
exec "$REPORT_SH" "$@"
REPORT_TOOL
chmod +x "$report_tools/sh"
snapshot "$fresh" > "$scratch/before-report-hash"
for report_record in old new; do
    if test "$report_record" = old; then
        report_file=$fresh/state/packages/app.tsv; report_at=1
    else
        # Descriptor validation hashes the proposed record once before the receipt.
        report_file=$next/package.tsv; report_at=2
    fi
    for report_output in empty digest; do
        printf '0\n' > "$scratch/report-count"
        reject env PATH="$report_tools:$PATH" REPORT_SH="$report_sh" REPORT_FILE="$report_file" \
            REPORT_COUNT="$scratch/report-count" REPORT_FAIL_AT="$report_at" REPORT_OUTPUT="$report_output" \
            sh mk/binary.sh preflight "$fresh" "$next" "$next_pin" test-host-v1
        grep '^injected-preflight-receipt-hash-error$' "$scratch/err" >/dev/null
        test ! -s "$scratch/out"
        snapshot "$fresh" > "$scratch/after-report-hash"
        cmp "$scratch/before-report-hash" "$scratch/after-report-hash"
    done
done
printf 'Four preflight receipt hash failures reject without report bytes or target changes\n'
# Failed producers/sorts cannot turn partial output into a successful preflight.
fault_tools=$scratch/preflight-tools
mkdir "$fault_tools"
real_awk=$(command -v awk)
real_sort=$(command -v sort)
cat > "$fault_tools/awk" <<'FAULT_TOOL'
#!/bin/sh
seam=
for argument do
    case $argument in
        */update-diff.awk) seam=diff ;;
        */update-three-way.awk) seam=three-way ;;
        '$1=="file" {print $4}') seam=observe ;;
        */changes.unsorted) seam=diff-sort ;;
        */three-way.unsorted) seam=three-way-sort ;;
        */paths.unsorted) seam=observe-sort ;;
    esac
done
if test "$seam" = "$FAULT_SEAM"; then
    printf 'injected-preflight-failure\n' >&2
    if test "$FAULT_OUTPUT" = partial; then printf 'partial\n'; fi
    exit 73
fi
case $0 in */awk) exec "$REAL_AWK" "$@" ;; *) exec "$REAL_SORT" "$@" ;; esac
FAULT_TOOL
cp "$fault_tools/awk" "$fault_tools/sort"
chmod +x "$fault_tools/awk" "$fault_tools/sort"
snapshot > "$scratch/before-faults"
for seam in diff three-way observe diff-sort three-way-sort observe-sort; do
    for fault_output in empty partial; do
        reject env PATH="$fault_tools:$PATH" REAL_AWK="$real_awk" REAL_SORT="$real_sort" \
            FAULT_SEAM="$seam" FAULT_OUTPUT="$fault_output" \
            sh mk/binary.sh preflight "$fresh" "$next" "$next_pin" test-host-v1
        test ! -s "$scratch/out" || { printf 'FAIL: partial preflight report escaped\n' >&2; exit 1; }
        grep 'injected-preflight-failure' "$scratch/err" >/dev/null
        snapshot > "$scratch/after-faults"
        cmp "$scratch/before-faults" "$scratch/after-faults"
    done
done
printf 'Twelve preflight producer/sort faults reject without reports or target changes\n'

snapshot > "$scratch/before-preflight"
preflight > "$scratch/preflight"
printf 'report\tupdate-preflight-v1\tnon-mutating\npackage\tapp\nold-record\t%s\nnew-record\t%s\n' \
    "$(hash "$fresh/state/packages/app.tsv")" "$(hash "$next/package.tsv")" > "$scratch/expected-report-header"
sed -n '1,4p' "$scratch/preflight" > "$scratch/actual-report-header"
cmp "$scratch/expected-report-header" "$scratch/actual-report-header"
grep '^version.*0.1.*0.2$' "$scratch/preflight" >/dev/null
grep '^content-change.*app$' "$scratch/preflight" >/dev/null
grep '^mode-change.*app$' "$scratch/preflight" >/dev/null
grep '^remove.*obsolete$' "$scratch/preflight" >/dev/null
grep '^add.*new.conf$' "$scratch/preflight" >/dev/null
grep '^result.*no-blockers-detected$' "$scratch/preflight" >/dev/null
snapshot > "$scratch/after-preflight"
cmp "$scratch/before-preflight" "$scratch/after-preflight"
# Locally changed bytes are reported and preserved, never overwritten.
printf '\nlocal edit\n' >> "$fresh/stage/app/app"
snapshot > "$scratch/before-preflight"
code=0
preflight > "$scratch/drift-preflight" || code=$?
test "$code" -eq 2
grep '^blocker.*installed-drift' "$scratch/drift-preflight" >/dev/null
snapshot > "$scratch/after-preflight"
cmp "$scratch/before-preflight" "$scratch/after-preflight"
cp -p "$source_root/stage/app/app" "$fresh/stage/app/app"
# Three-way classification keeps matching local edits blocked until an apply policy exists.
next_digest=$(awk -F '\t' '$1=="file" && $4=="app" {print $2}' "$next/package.tsv")
cp "$next/files/$next_digest" "$fresh/stage/app/app"
chmod 0700 "$fresh/stage/app/app"
code=0
preflight > "$scratch/matching" || code=$?
test "$code" -eq 2
grep '^three-way.*matching-change.*app$' "$scratch/matching" >/dev/null
cp -p "$source_root/stage/app/app" "$fresh/stage/app/app"
# An unowned local configuration at a proposed new path is never overwritten.
printf 'local=yes\n' > "$fresh/stage/app/new.conf"
code=0
preflight > "$scratch/config-conflict" || code=$?
test "$code" -eq 2
grep '^three-way.*conflict.*new.conf$' "$scratch/config-conflict" >/dev/null
test "$(cat "$fresh/stage/app/new.conf")" = local=yes
rm "$fresh/stage/app/new.conf"
host_path=usr/local/share/pkg-mgr/app/host.kv
printf '# local note\n' >> "$fresh/stage/app/$host_path"
code=0
preflight > "$scratch/local-only" || code=$?
test "$code" -eq 2
grep '^three-way.*local-only.*host.kv$' "$scratch/local-only" >/dev/null
cp -p "$source_root/stage/app/$host_path" "$fresh/stage/app/$host_path"
ln -s "$scratch/world" "$fresh/stage/app/new.conf"
code=0
preflight > "$scratch/uninspectable" || code=$?
test "$code" -eq 2
grep '^three-way.*uninspectable.*new.conf$' "$scratch/uninspectable" >/dev/null
test -L "$fresh/stage/app/new.conf"
rm "$fresh/stage/app/new.conf"
grep '^three-way.*package-only.*obsolete$' "$scratch/preflight" >/dev/null
printf 'Three-way matching/local/package/conflicting and unsafe-path decisions passed\n'
# Explicit retained replacement: prepare once, exercise each publication boundary.
prepared=$scratch/prepared
cp -Rp "$fresh" "$prepared"
old_pin=$(hash "$prepared/state/packages/app.tsv")
reject sh mk/replacement.sh prepare "$prepared" "$next" "$next_pin" test-host-v1 "$next_pin"
test ! -e "$prepared/.replacement"
# cmp status 1 means different; tool/read errors must not select a branch.
cmp_tools=$scratch/cmp-tools
mkdir "$cmp_tools"
real_cmp=$(command -v cmp)
cat > "$cmp_tools/cmp" <<'CMP_TOOL'
#!/bin/sh
if test "$#" -eq 3 && test "$1" = -s && test "$2" = "$CMP_LEFT" && test "$3" = "$CMP_RIGHT"; then
    count=0
    if test -f "$CMP_COUNT"; then read -r count < "$CMP_COUNT"; fi
    count=$((count + 1))
    printf '%s\n' "$count" > "$CMP_COUNT"
    if test "$count" -eq "$CMP_FAIL_AT"; then
        printf 'injected-record-comparison-error\n' >&2
        exit "$CMP_ERROR"
    fi
fi
exec "$REAL_CMP" "$@"
CMP_TOOL
chmod +x "$cmp_tools/cmp"
snapshot "$prepared" > "$scratch/before-cmp"
for cmp_error in 2 73; do
    for cmp_action in preflight prepare; do
        printf '0\n' > "$scratch/cmp-count"
        # The prepare branch repeats the pair after its required preflight.
        if test "$cmp_action" = preflight; then cmp_at=1; else cmp_at=2; fi
        if test "$cmp_action" = preflight; then
            set -- sh mk/binary.sh preflight "$prepared" "$next" "$next_pin" test-host-v1
        else
            set -- sh mk/replacement.sh prepare "$prepared" "$next" "$next_pin" test-host-v1 "$old_pin"
        fi
        reject env PATH="$cmp_tools:$PATH" REAL_CMP="$real_cmp" CMP_LEFT="$prepared/state/packages/app.tsv" \
            CMP_RIGHT="$next/package.tsv" CMP_COUNT="$scratch/cmp-count" CMP_FAIL_AT="$cmp_at" CMP_ERROR="$cmp_error" "$@"
        test ! -s "$scratch/out"
        grep 'cannot compare package records' "$scratch/err" >/dev/null
        grep 'injected-record-comparison-error' "$scratch/err" >/dev/null
        test ! -e "$prepared/.replacement"
        snapshot "$prepared" > "$scratch/after-cmp"
        cmp "$scratch/before-cmp" "$scratch/after-cmp"
    done
done
# Every intent digest must succeed before publishing or accepting the intent.
intent_tools=$scratch/intent-tools
mkdir "$intent_tools"
real_sh=$(command -v sh)
cat > "$intent_tools/sh" <<'INTENT_TOOL'
#!/bin/sh
if test "$#" -eq 3 && test "${1##*/}" = verify-metadata.sh && test "$2" = hash-file; then
    case $3 in
        */transaction/"$INTENT_FIELD"|*/.replacement/"$INTENT_FIELD")
            printf 'injected-intent-hash-error\n' >&2
            exit 73 ;;
    esac
fi
exec "$REAL_SH" "$@"
INTENT_TOOL
chmod +x "$intent_tools/sh"
snapshot "$prepared" > "$scratch/before-intent"
for intent_field in old-record new-record world others.tsv bundle/artifact.kv; do
    reject env PATH="$intent_tools:$PATH" REAL_SH="$real_sh" INTENT_FIELD="$intent_field" \
        sh mk/replacement.sh prepare "$prepared" "$next" "$next_pin" test-host-v1 "$old_pin"
    test ! -s "$scratch/out"
    grep '^injected-intent-hash-error$' "$scratch/err" >/dev/null
    test ! -e "$prepared/.replacement"
    snapshot "$prepared" > "$scratch/after-intent"
    cmp "$scratch/before-intent" "$scratch/after-intent"
done
# Reuse this real validated package pair for CLI receipt-loss/recovery coverage.
python3 tests/cli-receipt.py "$fresh" "$next" "$next_pin" "$old_pin"
sh mk/replacement.sh prepare "$prepared" "$next" "$next_pin" test-host-v1 "$old_pin" > "$scratch/prepared-output"
intent_pin=$(awk -F '\t' '$1=="prepared"{print $3}' "$scratch/prepared-output")
snapshot "$prepared" > "$scratch/before-cmp-finish"
for cmp_error in 2 73; do
    printf '0\n' > "$scratch/cmp-count"
    reject env PATH="$cmp_tools:$PATH" REAL_CMP="$real_cmp" CMP_LEFT="$prepared/state/packages/app.tsv" \
        CMP_RIGHT="$prepared/.replacement/old-record" CMP_COUNT="$scratch/cmp-count" CMP_FAIL_AT=1 CMP_ERROR="$cmp_error" \
        sh mk/replacement.sh finish "$prepared" "$intent_pin"
    test ! -s "$scratch/out"
    grep 'cannot compare package records' "$scratch/err" >/dev/null
    grep 'injected-record-comparison-error' "$scratch/err" >/dev/null
    snapshot "$prepared" > "$scratch/after-cmp-finish"
    cmp "$scratch/before-cmp-finish" "$scratch/after-cmp-finish"
done
for intent_field in old-record new-record world others.tsv bundle/artifact.kv; do
    reject env PATH="$intent_tools:$PATH" REAL_SH="$real_sh" INTENT_FIELD="$intent_field" \
        sh mk/replacement.sh finish "$prepared" "$intent_pin"
    test ! -s "$scratch/out"
    grep '^injected-intent-hash-error$' "$scratch/err" >/dev/null
    snapshot "$prepared" > "$scratch/after-intent"
    cmp "$scratch/before-cmp-finish" "$scratch/after-intent"
done
printf 'Ten replacement intent hash errors reject without publication or target changes\n'
printf 'Six record-comparison errors reject before reports or target changes\n'
reject sh mk/state.sh list "$prepared"
reject make -s -f mk/pkg.mk ROOT="$prepared" package
cat > "$scratch/bin/mv" <<'WRAPPER'
#!/bin/sh
for arg do
    if test "$arg" = "$FAIL_DEST"; then
        if test "${KILL_BEFORE:-no}" = yes; then kill -KILL "$PPID"; exit 1; fi
        "$REAL_MV" "$@" || exit
        kill -KILL "$PPID"
        exit 1
    fi
done
exec "$REAL_MV" "$@"
WRAPPER
for boundary in displaced staged record-copy recorded archived; do
    replacing=$scratch/replace-$boundary
    cp -Rp "$prepared" "$replacing"
    case $boundary in
        displaced) destination=$replacing/.replacement/previous ;;
        staged) destination=$replacing/stage/app ;;
        record-copy|recorded) destination=$replacing/state/packages/app.tsv ;;
        archived) destination=$replacing/replacements/$intent_pin ;;
    esac
    kill_before=no
    test "$boundary" != record-copy || kill_before=yes
    interrupted_status=0
    env PATH="$scratch/bin:$PATH" REAL_MV="$real_mv" KILL_BEFORE="$kill_before" FAIL_DEST="$destination" \
        sh mk/replacement.sh finish "$replacing" "$intent_pin" > "$scratch/out" 2> "$scratch/err" || interrupted_status=$?
    test "$interrupted_status" -gt 128
    test "$(kill -l "$interrupted_status")" = KILL
    test ! -s "$scratch/out"
    if test "$boundary" != archived; then reject sh mk/state.sh verify "$replacing"; fi
    sh mk/replacement.sh finish "$replacing" "$intent_pin" >/dev/null
    sh mk/replacement.sh finish "$replacing" "$intent_pin" >/dev/null
    cmp "$next/package.tsv" "$replacing/state/packages/app.tsv"
    cmp "$fresh/state/packages/base.tsv" "$replacing/state/packages/base.tsv"
    cmp "$fresh/state/world" "$replacing/state/world"
    cmp "$fresh/state/packages/app.tsv" "$replacing/replacements/$intent_pin/old-record"
    cmp "$fresh/stage/app/obsolete" "$replacing/replacements/$intent_pin/previous/obsolete"
    test ! -e "$replacing/stage/app/obsolete"
    test -f "$replacing/stage/app/new.conf"
    sh mk/state.sh verify "$replacing" >/dev/null
done
# Inject ordinary storage-operation failures without filling a host filesystem.
# Both injections occur after payload movement but before record publication.
fault_bin=$scratch/storage-fault-bin
mkdir "$fault_bin"
real_cp=$(command -v cp)
cat > "$fault_bin/cp" <<'WRAPPER'
#!/bin/sh
if test "$#" -eq 2 && test "$2" = "$FAIL_DEST"; then
    dd if="$1" of="$2" bs=1 count=17 2>/dev/null || exit 74
    printf 'injected-partial-record-copy\n' >&2
    exit 73
fi
exec "$REAL_CP" "$@"
WRAPPER
cat > "$fault_bin/mv" <<'WRAPPER'
#!/bin/sh
if test "$#" -eq 2 && test "$2" = "$FAIL_DEST"; then
    printf 'injected-record-rename-failure\n' >&2
    exit 73
fi
exec "$REAL_MV" "$@"
WRAPPER
chmod 0755 "$fault_bin/cp" "$fault_bin/mv"
for failure in partial-copy rename; do
    replacing=$scratch/storage-$failure
    cp -Rp "$prepared" "$replacing"
    case $failure in
        partial-copy) destination=$replacing/.replacement/record-publishing ;;
        rename) destination=$replacing/state/packages/app.tsv ;;
    esac
    code=0
    env PATH="$fault_bin:$PATH" REAL_CP="$real_cp" REAL_MV="$real_mv" FAIL_DEST="$destination" \
        sh mk/replacement.sh finish "$replacing" "$intent_pin" > "$scratch/out" 2> "$scratch/err" || code=$?
    test "$code" -eq 73
    case $failure in
        partial-copy) grep '^injected-partial-record-copy$' "$scratch/err" >/dev/null ;;
        rename) grep '^injected-record-rename-failure$' "$scratch/err" >/dev/null ;;
    esac
    cmp "$fresh/state/packages/app.tsv" "$replacing/state/packages/app.tsv"
    cmp "$fresh/state/packages/base.tsv" "$replacing/state/packages/base.tsv"
    cmp "$fresh/state/world" "$replacing/state/world"
    cmp "$fresh/stage/app/obsolete" "$replacing/.replacement/previous/obsolete"
    test -f "$replacing/stage/app/new.conf"
    test ! -e "$replacing/replacements/$intent_pin"
    reject sh mk/state.sh verify "$replacing"
    if test "$failure" = partial-copy; then
        test "$(wc -c < "$replacing/.replacement/record-publishing" | tr -d ' ')" -eq 17
        partial_pin=$(hash "$replacing/.replacement/record-publishing")
        reject sh mk/replacement.sh finish "$replacing" "$intent_pin"
        grep '^replacement-error: invalid pending record copy$' "$scratch/err" >/dev/null
        test "$(hash "$replacing/.replacement/record-publishing")" = "$partial_pin"
        cmp "$fresh/state/packages/app.tsv" "$replacing/state/packages/app.tsv"
    else
        cmp "$next/package.tsv" "$replacing/.replacement/record-publishing"
        sh mk/replacement.sh finish "$replacing" "$intent_pin" >/dev/null
        sh mk/replacement.sh finish "$replacing" "$intent_pin" >/dev/null
        cmp "$next/package.tsv" "$replacing/state/packages/app.tsv"
        cmp "$fresh/stage/app/obsolete" "$replacing/replacements/$intent_pin/previous/obsolete"
        sh mk/state.sh verify "$replacing" >/dev/null
    fi
done
printf 'Partial record copy preserves blocked evidence; failed record rename retries safely\n'
# Stale payload and changed world after preparation are preserved and refused.
printf stale >> "$prepared/stage/app/app"
# finish suppresses the shadow verifier report; prove the mutation's exact cause separately.
# Pending transactions block ordinary state inspection; use only a private probe copy.
stale_probe=$scratch/stale-probe
cp -Rp "$prepared" "$stale_probe"
mv "$stale_probe/.replacement" "$scratch/stale-probe-intent"
stale_status=0
sh mk/state.sh verify "$stale_probe" > "$scratch/out" 2> "$scratch/err" || stale_status=$?
test "$stale_status" -eq 1
printf 'size-mismatch\tapp\tapp\n' > "$scratch/expected-stale"
cmp "$scratch/expected-stale" "$scratch/out"
test ! -s "$scratch/err"
snapshot "$prepared" > "$scratch/before-stale"
stale_status=0
sh mk/replacement.sh finish "$prepared" "$intent_pin" > "$scratch/out" 2> "$scratch/err" || stale_status=$?
test "$stale_status" -eq 1
test ! -s "$scratch/out"
test ! -s "$scratch/err"
snapshot "$prepared" > "$scratch/after-stale"
cmp "$scratch/before-stale" "$scratch/after-stale"
test ! -e "$prepared/.replacement/previous"
cp -p "$fresh/stage/app/app" "$prepared/stage/app/app"
printf '# changed world\n' >> "$prepared/state/world"
snapshot "$prepared" > "$scratch/before-world"
stale_status=0
sh mk/replacement.sh finish "$prepared" "$intent_pin" > "$scratch/out" 2> "$scratch/err" || stale_status=$?
test "$stale_status" -eq 1
test ! -s "$scratch/out"
printf 'replacement-error: world changed since preparation\n' > "$scratch/expected-world"
cmp "$scratch/expected-world" "$scratch/err"
snapshot "$prepared" > "$scratch/after-world"
cmp "$scratch/before-world" "$scratch/after-world"
test ! -e "$prepared/.replacement/previous"
printf 'Retained replacement and five killed publication points passed\n'
# A changed base record has a reverse dependent and needs a coordinated plan.
rm "$updated/state/packages/base.tsv"
sed 's/^version=.*/version=0.2/' "$scratch/base/input.kv" > "$scratch/base/input2.kv"
sh mk/verify-metadata.sh build-record "$scratch/base/input2.kv" "$scratch/base/build2.kv" >/dev/null 2>&1
# Remove only the test copy's app authority to let the base fixture register.
rm "$updated/state/packages/app.tsv"
sh mk/state.sh register "$updated" "$scratch/base/manifest.tsv" "$scratch/base/build2.kv" "$scratch/base/deps" >/dev/null
sh mk/binary.sh export "$updated" base >/dev/null
pin=$(hash "$updated/binaries/base/artifact.kv")
code=0
sh mk/binary.sh preflight "$fresh" "$updated/binaries/base" "$pin" test-host-v1 > "$scratch/reverse-preflight" || code=$?
test "$code" -eq 2
grep '^blocker.*reverse-dependent.*app$' "$scratch/reverse-preflight" >/dev/null
printf 'Second-version preflight, drift preservation and reverse-dependent blocking passed\n'
# A package present only at the destination owns the proposed new path.
mkdir -p "$fresh/stage/spare"
printf owned > "$fresh/stage/spare/new.conf"
manifest=$scratch/spare.manifest
sh mk/verify-metadata.sh manifest "$fresh/stage/spare" "$manifest" >/dev/null
REF=${manifest#"$repo/"} awk '
 /^package_name=/ {print "package_name=spare"; next}
 /^manifest_ref=/ {print "manifest_ref=" ENVIRON["REF"]; next}
 {print}' fixtures/metadata-boundary/build-input.kv > "$scratch/spare.input"
sh mk/verify-metadata.sh build-record "$scratch/spare.input" "$scratch/spare.build" >/dev/null 2>&1
: > "$scratch/spare.deps"
sh mk/state.sh register "$fresh" "$manifest" "$scratch/spare.build" "$scratch/spare.deps" >/dev/null
snapshot > "$scratch/before-preflight"
reject preflight
grep 'state-conflict' "$scratch/err" >/dev/null
test ! -s "$scratch/out"
snapshot > "$scratch/after-preflight"
cmp "$scratch/before-preflight" "$scratch/after-preflight"
printf 'Update ownership conflict rejected without target mutation\n'
