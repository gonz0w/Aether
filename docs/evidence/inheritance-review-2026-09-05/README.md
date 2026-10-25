# UP-01 host ownership evidence

2026-09-05. [Review and reproduction](../../NATIVE-INHERITANCE-REVIEW.md).
Twelve host workloads pass. Three private model mutations reject at designated
assertions: a frozen shared offset, premature final-close obligation, and rights
widening during inheritance. The scripts record the exact source substitutions;
none changes working source. Full host tests and all three offline standards
checks pass, including 56 Python test methods.

`summary.json` pins source copies and mutation logs; `host.log` retains the full
development run. An initial early-close control reached a KeyError after a second
alias close; the final test checks the close obligation immediately after the
first alias removal, so the retained control fails its semantic assertion instead.

This is a synthetic host model with trusted caller selection and supplied backend
completion counts. It does not implement native authentication, IPC, actual file
I/O, backend close, concurrency, fork/exec or POSIX inheritance. No QEMU run,
companion adoption, shared owner approval or new ABI is claimed. Sys-init's
existing kernel-fix handoff and userland/package consumption remain distinct.
