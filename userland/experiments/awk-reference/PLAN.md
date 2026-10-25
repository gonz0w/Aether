# UL-066 awk consumer comparison

2026-09-06, contributor research. Build three source-pinned providers with the
same Clang 21.1.8 on macOS arm64. This first comparison isolates actual package
script behavior from musl/native porting. It makes no Linux/native, performance
or security-superiority claim. Final Clang/musl builds and upstream full suites
remain required before provider admission.

Inputs: source lock, immutable copies of package-manager awk files plus notices,
explicit generated fixtures. Test schema names/rejections, renderer escaping,
update-diff and three-way decisions under LC_ALL=C with independently stated
outputs and exit status. Retain every attempt. Compare sets only for documented
unordered awk array output. Keep diagnostics and output streams distinct.

Apply E-01–08, PX-01–04, CD-01/04, CP, TD-01/TC/TE and DP. Build tools are pinned
Clang plus host SDK/make/parser tools recorded in evidence. Private build roots,
no real-prefix install, no hidden fetch, bounded build subprocess groups and
15-second fixture deadlines. Fixed scripts may open only fixture files and
/dev/stderr; no shell/system expressions are supplied. New input drift rejects.

GNU optional extensions/readline/MPFR are excluded from this host comparison
where configure supports it. Retain configure help, warnings and actual closure;
absence of an option is not successful disabling. Independent reviewer pending.
Source authenticity/post-release security review remains UL-016. No release
exception or source relicense. tr/stty narrow through primary documentation;
full implementation comparison remains explicit follow-on if not exercised here.
