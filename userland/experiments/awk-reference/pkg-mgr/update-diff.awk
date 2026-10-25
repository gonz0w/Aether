# Both records have passed strict schema and evidence validation.
BEGIN {FS=OFS="\t"}
FILENAME==ARGV[1] {
    if($1=="package") old_version=$3
    if($1=="file") {old[$4]=$2 FS $3; oldmode[$4]=$5}
    if($1=="dependency") olddep[$2]=1
    next
}
$1=="package" {print "version",old_version,$3}
$1=="dependency" {newdep[$2]=1}
$1=="file" {
    seen[$4]=1
    if(!($4 in old)) print "add",$4
    else {
        if(old[$4]!=$2 FS $3) print "content-change",$4
        if(oldmode[$4]!=$5) print "mode-change",$4
    }
}
END {
    for(p in old) if(!(p in seen)) print "remove",p
    for(p in olddep) if(!(p in newdep)) print "dependency-remove",p
    for(p in newdep) if(!(p in olddep)) print "dependency-add",p
}
