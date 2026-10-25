/inputs/helper status &
p=$!
wait "$p"
s=$?
[ "$s" -eq 7 ] || exit 20
printf "wait ok\n"
