# Human presentation only. Machine mode bypasses this renderer completely.
BEGIN {FS="\t"; for(i=0;i<32;i++) control[sprintf("%c",i)]=i; control[sprintf("%c",127)]=127; if(plain=="yes") for(i=128;i<256;i++) control[sprintf("%c",i)]=i}
function safe(s, out,i,c) {
    out=""
    for(i=1;i<=length(s);i++) {c=substr(s,i,1); out=out (c in control ? sprintf("\\x%02x",control[c]) : c)}
    return out
}
diagnostic=="yes" {print "  " safe($0); next}
command=="list" {if(NR==1) print "Package  Version  Selection"; print safe($1) "  " safe($2) "  " safe($3); next}
$1=="verified" {print "Verified staged file contents and recorded permissions."; next}
$1=="prepared" {print "Prepared package: " safe($2); print "Intent SHA-256: " safe($3); print "Replacement is pending; use finish with this digest."; next}
$1=="completed" {print "Completed package: " safe($2); print "Intent SHA-256: " safe($3); print "Previous package retained."; next}
{line=safe($1); for(i=2;i<=NF;i++) line=line "  " safe($i); print line}
