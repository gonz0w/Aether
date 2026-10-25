[ "$(kill -l 10)" = USR1 ] || exit 26
trap 'printf "signal ok\n"' USR1
kill -USR1 $$
