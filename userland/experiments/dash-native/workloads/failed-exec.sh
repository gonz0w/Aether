/inputs/missing
a=$?
/inputs/not-executable
b=$?
[ "$a" -eq 127 ] && [ "$b" -eq 126 ] || exit 24
printf "exec errors ok\n"
