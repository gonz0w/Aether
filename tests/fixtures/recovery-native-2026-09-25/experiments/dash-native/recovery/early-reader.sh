# SPDX-License-Identifier: BSD-2-Clause
# UL-007 recovery input for dash with pipefail; execute in one parent, without -e.
recovery_parent=$$
set -o pipefail || exit 41
/inputs/helper pump | /inputs/helper one
pipeline_status=$?
[ "$pipeline_status" -eq 42 ] || exit 42
printf "epipe ok\n"
set +o pipefail || exit 41
/inputs/helper argv "a b" "*" || exit 43
printf "pipe data\n" | /inputs/helper copy | /inputs/helper copy || exit 44
/inputs/helper closed || exit 45
printf "closed ok\n"
[ "$$" = "$recovery_parent" ] || exit 46
printf "recovery diagnostic\n" >&2
printf "recovery ok\n"
exit 0
