[ "$x" = "argv ok" ] || exit 33; /inputs/helper closed || exit 35; printf "closed ok\n"; [ "$$" = "$session_parent" ] || exit 36; printf "session diagnostic\n" >&2; printf "session ok\n"; exit 0
