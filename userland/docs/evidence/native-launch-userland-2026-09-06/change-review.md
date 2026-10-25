# UL-058 NB-03 native launch framing

Plan: opt-in runner hooks exercise the owner's documented 22 complete-frame
rejection fields, exact errno and zero receipt before a valid aligned command.
Seven raw prefix cases (0/1/4/16/31/32/383) close only the sending endpoint with
parent alive; require broker1100+prefix/reclaimed0 and no terminal records.
Owner's existing allow_launch_version and pad_launch_eof mutations must be caught
at parent103 and104 respectively, broker970; generic panic/timeout cannot pass.
No owner source changes. Test-only raw endpoint access does not widen native
adapter semantics; buffers are synchronous and bounded. Default runner code is
unchanged after preprocessing. Compare five legacy ELF hashes.

Use reviewed combined producer with explicit --launch-controls. Keep existing
NB-01/02 and nine ordinary cases (27 total with ten new cases); separately run
nine original-pin and21 host regressions. Existing compiler/SDK/host tool pins,
owned processes, 30-second guest watchdog/180-second command limits and15-minute
suite budget apply. Retain every attempt, full source/diffs, raw contexts, hashes,
cleanup and quality checks. Current task technical review; independent review,
NB-04 and public parser/recovery remain pending. EOF rejection is not recovery.

Actual technical review: current task checked corpus regions against the pinned
wire contract, signed errno/zero receipt checks, bounded raw prefix transfer,
parent-live endpoint closure, forbidden-reply drain and exact terminal/EOF oracles.
All27 combined native cases pass; nine original-pin and21 host checks pass.
Thirteen existing ELFs identical; eight added clients inspected. No runtime
attempt failed. Format and Python grammar checks pass; independent review pending.
