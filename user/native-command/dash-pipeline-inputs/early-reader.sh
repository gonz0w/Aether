set -o pipefail
/inputs/helper pump | /inputs/helper one
s=$?
[ "$s" -eq 42 ] || exit 23
printf "epipe ok\n"
