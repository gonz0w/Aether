# Interrupted pipe creation review

Requirement: qualify unknown create outcomes on real native transports before
connecting pipes to dash. After committing the pipe, deliver zero, one or 31 of
the 32 response bytes, then close the reply writer. The private C adapter must
return EIO, retain its original signal mask, poison the transport, publish neither
descriptor nor output element, and refuse a second create locally. The owner must
observe exit92 and an empty request route before dropping the parent holders,
retiring the pipe, closing the three backend handles and reclaiming both tasks.
Repeat the complete parent/backend lifetime three times through the same owner: six
real reclaims, no child, no fabricated successful creation or wait acknowledgment.

Forbidden: retrying an unknown operation, partially publishing descriptors,
dropping holders on reply closure alone, reclaiming live tasks, double-closing
the already closed reply writer, or declaring a watchdog failure successful.
Keep the existing malformed-reply abort and successful transfer profiles intact.
A retained-holder mutant must fail retirement at2168 after the exact client exit92,
with zero reclaims. It must not be accepted for a generic timeout or panic.

Scope: Aether's private Rust dispatcher and C probe, plus connections harness
oracles. No kernel, SDK, sibling, released pin, ABI, resource limit or public
pipe API changes. O-02–05, I-01/03–06, E-01–08 and local Coding/Testing process
apply. Existing native transport calls borrow owned stack arrays; no new unsafe
boundary, allocation, service, dependency or signal mechanism is introduced.
The early error branch must retain real TLS checks, so its executable remains
valid for the existing copied-process loader. New header formatting uses pinned
clang-format21.1.8; Rust uses1.98.0/edition2024 with skip_children.

Selection: focused positive truncation cases and exact retained-holder rejection,
then complete connections and affected launch/console suites, host and harness
checks, scoped format and immutable pin checks. Freeze runtime sources during
qualification and preserve all attempts. Record owner bytes against16KiB.
Update STATE, ROADMAP, native reference and workflow gaps with observed scope.

Simplicity: reuse existing channel EOF and confirmed-terminal primitives instead
of adding a retry protocol or recovery service. A narrow failure branch is enough
for this test; future nonterminal recovery is not implied. No obsolete mechanism
can be removed yet because the existing malformed-reply rejection remains useful.
Abnormal child cleanup, native copy rollback, SIGPIPE, live-owner pipe-generation
reuse, actual dash substitution and full R1 assembly remain separate work.

Preflight correction: the first attempt completed two interrupted lifetimes and
four actual reclaims, but the unchanged native-copy kernel profile requires six.
Use three real interrupted lifetimes within the existing three-generation limit;
do not weaken that check, alter quotas or launch dummy tasks. Preserve attempt1
as a fixture-count mismatch, not a passing target run.
