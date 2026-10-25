# ADP-01-W04 release artifact guard

Add -Drelease-artifact=true as an explicit build-time exclusion gate. It rejects
all existing deliberate negative-control options when enabled, before executing
build steps. Default experiment behavior and kernel options/bytes stay unchanged.
Do not claim release readiness; assembled release owners must select this gate and
bind the actual build flags/artifact. No native API or pin changes. Test every
negative option through actual Zig graph evaluation and reject exact named option,
verify a positive guarded build and byte identity against an unguarded default.
Keep full negative-control regression behavior available outside the guarded build.
Document the required flag and nonclaims. Inventory every current boolean option
so new unclassified switches fail host review checks. No new runtime dependency.
