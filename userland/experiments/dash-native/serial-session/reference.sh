# SPDX-License-Identifier: BSD-2-Clause
session_parent=$$; /inputs/helper argv "a b" "*" || exit 31; printf "pipe data\n" | /inputs/helper copy | /inputs/helper copy || exit 32
x=$(/inputs/helper argv "a b" "*") || exit 33; [ "$x" = "argv ok" ] || exit 33; printf "substitution ok\n"; printf "pipe data\n" | /inputs/helper copy | /inputs/helper copy || exit 34
[ "$x" = "argv ok" ] || exit 33; /inputs/helper closed || exit 35; printf "closed ok\n"; [ "$$" = "$session_parent" ] || exit 36; printf "session diagnostic\n" >&2; printf "session ok\n"; exit 0
