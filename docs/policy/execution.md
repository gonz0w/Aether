# Aether execution policy

Canonical sections extracted from [PROJECT](../../PROJECT.md). Local policy is
bound to the containing source revision; external pins retain their own identities.
Existing owner change authority and all applicable contracts remain in force.
Commands and literal repository paths below keep their original working directory;
only Markdown links were rebased for this file.

## Bounded Zsh application trial —2026-10-25

The owner approved implementing and host-testing the separately reviewed
[application profile](https://github.com/gonz0w/Aether/issues/69): a distinct
1.5 MiB application ELF cap, 384 image-plus-existing-stack pages and 640 total
backing pages in each of five fork-capable application slots. The engine retains 8192 pages and
the owner retains 128. This assigns 45 MiB within the existing 64 MiB backing
reservation; 19 MiB remains ungranted. The selected application image window is
`0x200000..0x400000`. Existing capability, TLS, stack/bootstrap and ownership
checks remain binding; older profiles retain their defaults, selectors and seals.

At the admitted image limit, at least 256 backing pages remain for all later
runtime allocations, including TLS and allocator overhead. This is a bounded
trial resource decision, not evidence of Zsh heap/stack sufficiency. Routine
implementation and host verification follow the finite issue scope, required
checks and separate review. No guest, native prompt or ISO qualification is
authorized by this decision. Exact SDK/artifact qualification evidence stays local.
## AF09 diagnostic control review —2026-10-26

The owner reviewed and approved the concrete [issue75 diagnostic](https://github.com/gonz0w/Aether/issues/75)
from draft PR76/head `88a83fab808221cec5770b3db447d849478688ee`.
Introduce the compile-time `native-af09-drain` selector with default `none` and
exactly `file_prefix`, `exec_prefix`, `fork_prefix`, `stream`, `no_ack`,
`partial_ack`, `exit_deadline` and `pending_fragment`. Omitted/explicit `none`
retain ordinary behavior. This satisfies DEVELOPMENT's human-review requirement
for this closed non-boolean control; do not ask for the same review again.

Implementation, host verification and matched offline artifact preparation may
proceed under the [diagnostic contract](../../docs/NATIVE-AF09-DRAIN.md). Existing
profile/authority/resource limits, source freezes, cleanup, separate review and
major-handoff checks remain. This adds no runtime selector, guest permission,
resource exception, native sufficiency or release acceptance. A later guest
requires its concrete reviewed artifact and execution disposition.
## AF09 offline family budget —2026-10-26

The owner adopted a standing5400-second aggregate for the complete
[issue75](https://github.com/gonz0w/Aether/issues/75) offline admission/drain
family: file_prefix, exec_prefix, fork_prefix, stream, no_ack, partial_ack,
exit_deadline and pending_fragment, with twenty prepared roles in total.
One clock covers the whole selected suite from preflight through final input
verification, publication and owned cleanup; case and builder calls do not renew it.
Other target suites retain their1800-second ceilings.

Children remain180 seconds, live stdout/stderr4MiB each and compiler files16MiB.
Focused host300/complete host900 limits, source freezes, all tests, existing media
allowances, runtime authority/memory/request bounds and known cleanup stay binding.
This time-only default grants no guest, native sufficiency or release acceptance.

Earlier failed campaigns remain failed. Triage failures, correct their cause,
recheck affected inputs and obtain separate preflight review before a justified
fresh complete-family attempt. Do not blindly retry unchanged failed work or
replay unknown mutations. This standing default does not require another approval
for each ordinary corrective attempt inside its scope; a larger bound or another
consequential resource change remains the owner's decision.
