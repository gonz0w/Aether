# SPDX-License-Identifier: BSD-2-Clause
# Bounded binding grammar or conservative reverse closure; never execute input.
function hash(s) { return length(s)==64 && s !~ /[^0-9a-f]/ }
function path(s) {
    return length(s)>0 && length(s)<=1024 && s !~ /[^A-Za-z0-9._+ \/-]/ &&
        s !~ /^\// && s !~ /\/$/ && s !~ /\/\// && s !~ /(^|\/)\.\.?($|\/)/
}
BEGIN {
    if (mode=="binding") {
        split("format sdk_package sdk_record_sha256 input_receipt_path input_receipt_sha256 artifact_path artifact_sha256", keys, " ")
    } else if (mode=="closure") FS="\t"
    else exit 1
}
mode=="binding" {
    if (NR>7 || $0 !~ /^[ -~]*$/ || index($0,keys[NR] "=")!=1) {bad=1; next}
    value=substr($0,length(keys[NR])+2)
    if (NR==1 && value!="sdk-static-binding-v1") bad=1
    if (NR==2 && value!="aether-musl-sdk") bad=1
    if ((NR==3 || NR==5 || NR==7) && !hash(value)) bad=1
    if ((NR==4 || NR==6) && !path(value)) bad=1
    rows[NR]=$0
    next
}
mode=="closure" {
    if (FILENAME==ARGV[1]) records[$2]=$3
    else {edges[$1 SUBSEP $2]=1; if ($2=="aether-musl-sdk") {direct[$1]=1; selected[$1]=1}}
}
END {
    if (mode=="binding") {
        if (bad || NR!=7) exit 1
        for (i=1;i<=7;i++) print rows[i]
    } else if (mode=="closure") {
        do {
            changed=0
            for (edge in edges) {
                split(edge, pair, SUBSEP)
                if ((pair[2] in selected) && !(pair[1] in selected)) {selected[pair[1]]=1; changed=1}
            }
        } while (changed)
        for (name in selected) print "requalify\t" name "\t" (name in direct ? "direct" : "transitive") "\t" records[name]
    }
}
