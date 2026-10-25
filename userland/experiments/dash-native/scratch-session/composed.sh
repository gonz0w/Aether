# SPDX-License-Identifier: BSD-2-Clause
scratch_parent=$$
exec 3>/scratch/data || exit 61
exec 4>&3 || exit 62
printf A >&3 || exit 63
exec 3>&- || exit 62
printf B >&4 || exit 63
exec 4>&- || exit 62
(printf wrong >/inputs/denied) 2>&-
denied_status=$?
[ "$denied_status" -eq 2 ] || exit 64
printf "denied ok\n"
/inputs/helper copy </scratch/data || exit 65
printf "\n"
/inputs/helper argv "a b" "*" || exit 66
printf "pipe data\n" | /inputs/helper copy | /inputs/helper copy || exit 67
/inputs/helper closed || exit 68
printf "closed ok\n"
[ "$$" = "$scratch_parent" ] || exit 69
printf "scratch diagnostic\n" >&2 || exit 70
printf "scratch ok\n"
exit 0
