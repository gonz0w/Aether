# Manual review handoff: quality checker and documentation

The project maintainer approved this review packet with no findings on 2026-09-06.
The [approval record](../evidence/source-inventory-2026-09-06/maintainer-review.json)
binds the unchanged source/manual bytes and preserves the scope of that statement.
No detailed execution/visual logs were supplied; packaged lookup remains open.
The checklist below is retained as the reviewed scope and for later re-review.
Review the implementation at commit `152af26f`, and the current manual's matching
source identity in the qualification evidence. The earlier manual commit is
`296da995`; its direct-child limitation was revised by `152af26f`.

## Technical review

From the checkout root, inspect:

```sh
git show 152af26f -- docs/quality/check.py docs/quality/processes.py docs/quality/test-processes.py docs/check-standards.py docs/check-distribution.py docs/check-experience.py
```

Also read the reused [process helper](../../experiments/command-runner/process.py),
the [change plan](../evidence/quality-process-2026-09-06/PLAN.md), and the
[results and boundaries](../evidence/quality-process-2026-09-06/README.md).

Check these specific properties against source and actual evidence:

1. Release bytes are verified before copied code runs, including wrong-pin paths.
2. The top-level gate does not nest session owners; each reference execution has
   a defined owner, deadline, output bound and cleanup decision.
3. A nonzero exit, timeout, surviving descendant or incomplete cleanup cannot
   become success. Original bytes and receipts survive output replay failure.
4. Minimal child environments and delayed stream replay match the manual;
   output streams and established markers/statuses remain distinct.
5. The declared exclusions are acceptable for trusted host checks. Session escape,
   owner SIGKILL, all interruption schedules and total in-process validation time
   are not qualified. These limits must not become a broader security claim.

To reproduce host controls, run the following separately from the checkout root:

```sh
python3 -B docs/quality/test-processes.py
python3 -B docs/quality/check.py
python3 -B docs/quality/check.py --release
```

The process suite and normal gate should pass. Release preflight should return 1
with `FAILED: incomplete release entry`; a pass would require investigation.
Do not wrap one session-owning checker in another independently killed session
owner and infer cleanup of both. Tests retain their owned work under `build/`.
The [new interpreter qualification packet](../evidence/python-qualification-2026-09-06/README.md)
provides exact isolated Python paths and results for 3.10/3.12.

## Reader walkthrough

Treat this as a separate record from source review. Use only the
[manual reading instructions](../../man/README.md) and
[manual](../../man/man1/aether-userland-quality.1), without author coaching.

Try to discover the supported options, run the normal checker, interpret release
rejection, and explain how to respond to a pin mismatch without altering real
pins. Record unclear steps or unexpected outputs. Do not deliberately corrupt
production pins; private rejection fixtures already have technical evidence.

Inspect the retained 50/78-column terminal rendering and the local HTML produced
by mandoc. Check headings, examples, minus signs, wrapping and ordinary/narrow
layouts. The agent's browser policy rejected file URLs; user visual review is
still needed. This is not packaged Aether manual lookup, which remains separate.

## Return the review

Send findings here or create a local review note. Include:

- Reviewer name and date; exact commit and source/manual digest reviewed.
- Technical decision: accepted within stated scope, or changes requested.
- Commands/interpreter/platform, observed results and evidence paths.
- Findings with file/line or reproduction and their resolution status.
- Separate reader/visual observations, obstacles and required revisions.
- Explicit exclusions and remaining packaged/native checks.

An approval of this host change cannot close UL-061–063 generally or authorize
publication. Any relevant implementation/manual change after review invalidates
the affected portion and needs re-review. Keep the current review pending until
actual findings arrive; do not populate reviewer fields from this template.
