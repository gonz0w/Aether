# SPDX-License-Identifier: BSD-2-Clause
exec_parent=$$
/inputs/missing 2>&-
missing_status=$?
[ "$missing_status" -eq 127 ] || exit 51
/inputs/not-executable 2>&-
denied_status=$?
[ "$denied_status" -eq 126 ] || exit 52
printf "exec errors ok\n"
/inputs/helper argv "a b" "*" || exit 53
printf "pipe data\n" | /inputs/helper copy | /inputs/helper copy || exit 54
/inputs/helper closed || exit 55
printf "closed ok\n"
[ "$$" = "$exec_parent" ] || exit 56
printf "exec recovery diagnostic\n" >&2 || exit 57
printf "exec recovery ok\n"
exit 0
