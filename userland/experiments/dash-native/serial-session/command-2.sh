x=$(/inputs/helper argv "a b" "*") || exit 33; [ "$x" = "argv ok" ] || exit 33; printf "substitution ok\n"; printf "pipe data\n" | /inputs/helper copy | /inputs/helper copy || exit 34
