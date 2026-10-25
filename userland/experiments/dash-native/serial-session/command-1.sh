session_parent=$$; /inputs/helper argv "a b" "*" || exit 31; printf "pipe data\n" | /inputs/helper copy | /inputs/helper copy || exit 32
