# AF07 owner preparation — 2026-10-21

Separate fixed AF07/ABI29 candidate under decision0192/BG-067. Host policy and
native linked-code/stack evidence only; no native guest or independent sign-off.
See [candidate and exact intake handoff](../../../prototypes/native-filesystem-af07/README.md).

preparation.json binds commands, logs, exact tools, all30 engine manifest members,
unchanged old AF06 sources and external input identities, new source copies and
raw/ELF artifacts. Four host tests cover35 inherited failure scenarios and four
version scenarios, bootstrap ordering, partial/EAGAIN, budgets, normal engine
terminal with retained ready1 and returned-halt failure. Four compiling guard
omissions (version, generation, early readiness, terminal kind/status) each fail
the actual focused test. Native read-only inspection gives2072 code bytes and
1096/4088 scoped stack, nine reachable functions. It does not execute the owner.

prior-attempt1 retains the initial build/test logs and zero-test omission attempt:
the --exact filter lacked the tests:: prefix and returned0 after selecting zero
tests. Preparation correctly rejected that result. The final filter selects one
actual test and records a nonzero assertion failure for each omission. This was
a test invocation error, not native behavior or evidence of a passing omission.

local-checks.json records the full repository check. sha256.json seals every file
except itself; historical AF06 evidence and defaults are unchanged. No file-content
mutation, filesystem-backed shell, persistent package or device-durability claim.
Aether must supply fresh matched native composition/positive/failure witnesses;
then sys-init independently reviews that exact receipt. This handoff is local/unsent.
