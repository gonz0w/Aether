# Compare content + permissions. Absence participates in the same comparison.
BEGIN {FS=OFS="\t"}
FILENAME==ARGV[1] {if($1=="file") old[$4]=$2 FS $5; next}
FILENAME==ARGV[2] {if($1=="file") proposed[$4]=$2 FS $5; next}
$1=="observed" {
    p=$2
    before=(p in old ? old[p] : "absent")
    after=(p in proposed ? proposed[p] : "absent")
    local=($3=="absent" || $3=="unsupported" ? $3 : $3 FS $4)
    if(local=="unsupported") decision="uninspectable"
    else if(local==before && after==before) decision="unchanged"
    else if(local==before) decision="package-only"
    else if(after==before) decision="local-only"
    else if(local==after) decision="matching-change"
    else decision="conflict"
    if(decision!="unchanged") print "three-way",decision,p
}
