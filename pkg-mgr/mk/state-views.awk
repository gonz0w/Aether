# Derived views only. Input has already passed per-record schema/hash validation.
BEGIN { FS=OFS="\t" }
$1=="package" { packages[$2]=$3 }
$1=="root" { roots[$2]=1 }
$1=="dependency" { edges[$2 SUBSEP $3]=1 }
$1=="file" {
    if($5 in owners) { print "state-conflict: multiple owners for " $5 > "/dev/stderr"; failed=1 }
    owners[$5]=$2; hashes[$5]=$3; sizes[$5]=$4; permissions[$5]=$6
}
END {
    for(r in roots) if(!(r in packages)) { print "state-dangling: unknown world root " r > "/dev/stderr"; failed=1 }
    for(e in edges) { split(e,a,SUBSEP); if(!(a[2] in packages)) { print "state-dangling: missing dependency " a[2] > "/dev/stderr"; failed=1 } }
    for(p in owners) {
        n=split(p,parts,"/"); parent=parts[1]
        for(i=2;i<=n;i++) {
            if(parent in owners) { print "state-conflict: file used as directory " parent > "/dev/stderr"; failed=1 }
            parent=parent "/" parts[i]
        }
    }
    if(failed) exit 1
    if(query!="" && !(query in packages)) { print "state-unknown-package: " query > "/dev/stderr"; exit 1 }
    if(mode=="list") for(p in packages) print p,packages[p],(p in roots ? "explicit" : "dependency")
    if(mode=="owners") for(p in owners) print p,owners[p]
    if(mode=="files") for(p in owners) if(owners[p]==query) print p,hashes[p],sizes[p],permissions[p]
    if(mode=="deps" || mode=="rdeps") for(e in edges) { split(e,a,SUBSEP); if(mode=="deps" && a[1]==query) print a[2]; if(mode=="rdeps" && a[2]==query) print a[1] }
    if(mode=="orphans") {
        for(r in roots) live[r]=1
        do { changed=0; for(e in edges) { split(e,a,SUBSEP); if(a[1] in live && !(a[2] in live)) { live[a[2]]=1; changed=1 } } } while(changed)
        for(p in packages) if(!(p in live)) print "orphan",p
    }
}
