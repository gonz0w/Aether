# Scoped substitution oracle review

Verified frozen pipe-dash.rs checks argc4/envc4 and exact `/inputs/helper`, `argv`,
`a b`, `*` strings before replacement. The wrong-args control mutates the admitted
argument after this check. pipe-exec-client.c validates table, pipe grant,
generations, saved mask and removed FD10/FD11 before calling the unchanged helper;
normal return closes0/1/2. Skip-helper bypasses only that helper invocation.

The helper independently checks argument values and WITNESS. Owner pipe accounting
checks actual written/read bytes against `argv ok\n`, bounds cumulative counts,
and accepts EOF only after the expected bytes. The unchanged shell trims the
newline, compares the variable and writes `substitution ok\n`. Owner close_backend
checks exact output positions and reads those bytes back before closure.
Thus status0 alone cannot satisfy the oracle. Both controls reject premature EOF
with owner2175 and no child terminal claim. Full-generation positive supervision
requires child0/parent0/backend17 twice and six reclaims. Outer owned-process
cleanup is independently required even for expected zero-reclaim abort controls.

This is a scoped Codex review, not independent owner sign-off or a public SDK audit.
