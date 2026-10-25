x=$(/inputs/helper argv "a b" "*")
[ "$x" = "argv ok" ] || exit 21
printf "substitution ok\n"
