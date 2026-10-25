# Strict inert-data schemas; no shell evaluation. LC_ALL=C is set by the caller.
function bad(message) { print "state-record-invalid: " message > "/dev/stderr"; failed=1; exit 1 }
function id(s) { return s ~ /^[A-Za-z0-9][A-Za-z0-9._+-]*$/ }
function hash(s) { return length(s)==64 && s !~ /[^0-9a-f]/ }
function path(s, n,a,i) {
    if (s !~ /^[A-Za-z0-9._+ \/-]+$/) return 0
    n=split(s,a,"/"); for(i=1;i<=n;i++) if(a[i]=="" || a[i]=="." || a[i]=="..") return 0
    return 1
}
function build(key,value) {
    if(key != keys[++build_count]) bad("unknown, missing, duplicate, or unordered build key")
    if(value=="" || value ~ /[^ -~]/) bad("invalid build value")
    evidence[key]=value
}
function check_build() {
    if(build_count!=key_count) bad("incomplete build evidence")
    if(evidence["record_type"]!="build" || !id(evidence["package_name"]) || !id(evidence["version"])) bad("build identity")
    if(evidence["source_hash_alg"]!="sha256" || !hash(evidence["source_hash"])) bad("source hash")
    if(substr(evidence["manifest_hash"],1,7)!="sha256:" || !hash(substr(evidence["manifest_hash"],8))) bad("manifest hash")
    if(evidence["provenance_confidence"]!="advisory" || evidence["verification_result"]!="warn" || evidence["result_label"]!="reproducible-build-success-not-proven") bad("unsupported evidence claims")
}
BEGIN {
    FS="\t"
    key_count=split("record_type repo_origin namespace package_name version recipe_path recipe_revision source_hash_alg source_hash manifest_hash materials_ref material_path sbom_ref builder_label phase_label command_label provenance_confidence verification_result result_label",keys," ")
}
mode=="build" {
    eq=index($0,"="); if(!eq) bad("build line lacks equals")
    build(substr($0,1,eq-1),substr($0,eq+1)); next
}
mode=="names" {
    if($0=="" || substr($0,1,1)=="#") next
    if(!id($0) || seen[$0]++) bad("invalid or duplicate package name")
    print; next
}
mode=="record" {
    if(NR==1) { if($0!="format\tpkg-state-v1" && $0!="format\tpkg-state-v2") bad("format"); v2=($2=="pkg-state-v2"); next }
    if(NR==2) {
        if(NF!=3 || $1!="package" || !id($2) || !id($3) || $2!=expected) bad("package identity")
        name=$2; version=$3; next
    }
    if(NR==3) { if(NF!=2 || $1!="build-record" || !hash($2)) bad("build fingerprint"); next }
    if(NR<=3+key_count) {
        if(NF!=3 || $1!="evidence") bad("build evidence")
        build($2,$3); next
    }
    if($1=="dependency") {
        if(files || NF!=2 || !id($2) || ("x" $2)<=("x" previous_dep)) bad("dependency order or name")
        previous_dep=$2; next
    }
    if($1=="file") {
        if(NF!=(v2 ? 5 : 4) || (v2 && $5!~/^0[0-7][0-7][0-7]$/) || !hash($2) || $3!~/^(0|[1-9][0-9]*)$/ || !path($4) || ("x" $4)<=("x" previous_path)) bad("file row or order")
        previous_path=$4; files++; next
    }
    bad("unknown record row")
}
END {
    if(failed) exit 1
    if(mode=="build" || mode=="record") check_build()
    if(mode=="record" && (NR<3+key_count || name!=evidence["package_name"] || version!=evidence["version"])) bad("record/evidence identity mismatch")
}
