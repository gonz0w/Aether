# Contributing to Aether

Thanks for taking an interest in this hobby OS. A clear reproduction, a confusing
paragraph explained, or a useful research note can help as much as a patch.

Public bug reports and feature requests are welcome in [Issues](https://github.com/gonz0w/Aether/issues).
Use [Discussions](https://github.com/gonz0w/Aether/discussions) for questions, open-ended design ideas and
sharing experiments. For vulnerabilities, use [private reporting](SECURITY.md).

## Pull requests for now

Only the repository owner, **@gonz0w**, opens pull requests at present. This keeps
implementation, review and integration manageable while the system takes shape.
Please open an issue or discussion instead of an unsolicited pull request. The
maintainer can turn an agreed contribution into a bounded implementation issue.
This policy can change through an explicit project decision.

CODEOWNERS identifies responsibility and review routing. It does not enforce who
may open a pull request, and it is not a claim that a change received review.

## Start with an issue

After the maintainer verifies onboarding and migration under
[PROJECT](PROJECT.md#public-onboarding-cutover), GitHub Issues are the sole
authority for live work, priority, dependencies, ownership and continuation.
Until then the one approved bootstrap record owns onboarding; this document does
not claim migration is complete or select work from historical queues. Read the whole issue and its discussion before starting; check
whether someone already owns it. A roadmap describes capability gates, and an old
planning record preserves context. Neither creates a second live work queue.

A useful implementation issue states:

- The problem and the observable result we want.
- The scope and what the change will leave out.
- Acceptance conditions and the focused checks that could demonstrate them.
- Real prerequisites, dependencies and the current owner.

Related tests belong with their change. There is no need to open an issue for
every assertion or mechanical step. Research and coordination issues can have
research deliverables rather than a code change.

The maintainer applies the pinned [GitHub work profile](.agent-temper/profiles/github.md).
An executable issue has one progress label: backlog, deferred, ready, in progress,
blocked or review. A proposal starts in backlog. Readiness does not expand an
issue's agreed resource, execution or release bounds. Preserve existing UL/BG
identifiers when linking older contracts to an issue.

## Reporting a bug

Search for an existing report first, then include the source revision, exact
command, host/tool versions, expected result and actual result. A short relevant
log excerpt helps. Keep the original failed attempt; a later successful retry
does not explain it.

Some native experiments depend on local sealed SDKs or service deliveries that
are not in the public source snapshot. Say which inputs were available. Missing
prerequisites, skipped checks and infrastructure failures are different from a
passing result.

Do not upload credentials, private data, SDK archives or generated disk/image
bundles to an issue. Share a compact redacted summary when logs contain sensitive
material. Potential vulnerabilities belong in the private reporting route.

## Development expectations

Read [PROJECT](PROJECT.md), [AGENTS](AGENTS.md), the pinned
[Agent Temper method](.agent-temper/METHOD.md), and the affected component guidance.
Follow the selected issue and its linked contracts. Read the
[public-source boundary](docs/PUBLIC-SOURCE.md): ordinary public prose and
self-contained model work use available local rules. Work needing private
standards or qualification inputs remains blocked until the owner supplies the
applicable inputs; missing checks are never reported as passes. The detailed
[development guide](docs/DEVELOPMENT.md) owns source conventions, test selection,
security review and compact evidence retention.

Keep changes small enough to understand and review. Preserve capability-based
access, explicit ownership and cleanup. Prefer user-space policy over expanding
the trusted kernel. Explain a new dependency, unsafe boundary, protocol or resource
cost before adding it.

Define expected behavior and forbidden outcomes before implementation. Use
meaningful tests first where feasible; record a missing prerequisite or a justified
alternative honestly. Run focused affected checks during iteration. Broad suites
belong at the integration gates selected by project policy. Keep sources frozen
through a qualified run and retain each attempt's compact results and failures.

In a pull request, explain the problem, resulting behavior, verification and
material limits. Use `Closes #NUMBER` only when that issue's entire acceptance is
satisfied. Do not auto-close an epic, partial work or a separate operational gate.
Implementation issues close on accepted merge, not when a PR opens.

Required separate review and checks precede integration. Hosted source checks,
peer review and local host tests each have their own scope; none establishes a
working OS release by itself.

## Licensing

Original contributions intentionally submitted for inclusion are offered under
[BSD-2-Clause](LICENSE), unless different terms are identified and accepted first.
Contributors retain copyright; no copyright assignment is requested.

Submit only work you have the right to contribute. Identify imported or derived
material and preserve its upstream license, attribution and provenance. A package
recipe does not relicense its payload. See [LICENSING](docs/LICENSING.md).
