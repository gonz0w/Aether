exec 9>/scratch/leak
/inputs/helper closed
s=$?
[ "$s" -eq 0 ] || exit 22
