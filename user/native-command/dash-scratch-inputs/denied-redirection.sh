(printf wrong >/inputs/denied)
s=$?
[ "$s" -ne 0 ] || exit 25
printf "denied ok\n"
