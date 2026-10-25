# pkg-mgr

This component lives in the Aether system repository. Commands here run from
this directory unless stated otherwise. Start with the pinned [Agent Temper
method](../.agent-temper/METHOD.md), root [engineering policy](../PROJECT.md) and
[public work navigation](../.planning/STATE.md#system-work-index). Under
[root PROJECT cutover policy](../PROJECT.md#public-onboarding-cutover), GitHub
Issues own live work only after verified onboarding/migration. Until then only
the approved bootstrap record owns onboarding. STATE is navigation; component
snapshots and all dated next actions below are read-only historical context.
Local qualification receipts/SDK bundles are excluded from the public snapshot;
a summary is not a public replay or a fresh validation. See the
[repository guide](../docs/REPOSITORY.md) for dependencies and checkout boundaries.
Standards releases/review snapshots and imported hooks remain private; see the
[public-source boundary](../docs/PUBLIC-SOURCE.md). Ordinary public documentation
uses available local policy; affected normative work requires the owner and exact
private inputs. Aggregates that require those inputs remain blocked without them.


An experimental source-and-binary package manager for Aether, with host tooling for development. The design starts with readable recipes, shell, make, and plain records; complexity must earn its place through working evidence.

**Current status:** pinned static zlib and a dependent compression utility build, test, stage, and register on the host, then export/import into a fresh private root without rebuilding. Plain package records, editable roots, inspection, and verification work. A separate boot-artifact handoff passes Aether’s two-CPU smoke test. Retained replacement now works in private roots. Live installation, payload deletion, and sys-init activation remain unimplemented.

**Release target:** Aether only. Host checks are development evidence; native
package-manager execution and storage acceptance remain unproven. Cam owns the
pending reviews. See [Aether release acceptance](docs/AETHER-RELEASE.md).

## Start here

- [CLI usage](docs/CLI.md): inspect, import, compare, and finish private-root replacements.
- [Project direction](.planning/PROJECT.md): goals and boundaries.
- [Architecture and integration](docs/ARCHITECTURE.md): current command path, Aether, and sys-init responsibilities.
- [Roadmap](.planning/ROADMAP.md): component capability gates and candidate details.
- [Real source packages](docs/ZLIB-PACKAGE.md): zlib and its dependent utility.
- [Local binary transport](docs/BINARY-PACKAGE.md): integrity, target checks, and runnable imported packages.
- [Interrupted-import recovery](docs/IMPORT-RECOVERY.md): explicit recovery and failure behavior.
- [Update preflight](docs/UPDATE-PREFLIGHT.md): compare a proposed replacement without changing installed state.
- [Configuration and replacement policy](docs/REPLACEMENT-POLICY.md): local-edit decisions, retained replacement, and recovery boundaries.
- [Launch/channel/file transport](docs/NATIVE-LAUNCH-TRANSPORT.md): pinned profile and independent userland channel witnesses.
- [Native-memory transport](docs/NATIVE-MEMORY-TRANSPORT.md): package-staged userland allocation/descriptor witness.
- [Aether handoff](docs/AETHER-HANDOFF.md): staged boot artifacts and recorded QEMU evidence.
- [Package-state commands](docs/PACKAGE-STATE.md): records, world, verification, and a runnable demo.
- [System work index](../.planning/STATE.md#system-work-index): selected bounded record and continuation.
- [Component history](.planning/STATE.md): dated evidence summaries.
- [September 5 review](docs/REVIEW-2026-09-05.md): findings and planning migration.

## Run the current checks

Select affected checks under root [DEVELOPMENT](../docs/DEVELOPMENT.md). When the
bounded aggregate is required or no safe subset exists, run from `pkg-mgr/`:

```sh
sh tests/check.sh
```

The runner checks all active shell files, copies the fixture into a temporary directory and runs sixteen local tests under a 600-second watchdog. It prints a private run directory retaining the log and result. Build tests create their own private output roots; the checkout's manifests and outputs remain untouched. Requires Python 3, ShellCheck 0.11.0 (development checks only), `sh`, GNU-compatible `make`, standard Unix text/file tools, and a SHA-256 tool (`sha256sum`, `shasum`, `sha256`, or `openssl`). `minisign` enables additional live signature checks; absence is reported as a skip.

Run the local demo from `pkg-mgr/`:

```sh
fixture_root=$(mktemp -d)
make -f mk/pkg.mk ROOT="$fixture_root" init-root
make -j8 -f mk/pkg.mk ROOT="$fixture_root" package
cat "$fixture_root/manifests/hello-local.manifest"
```

It verifies a copied input before extraction, stages one text file, and emits a path manifest. For a real source build and dependency demonstration, follow [the zlib workflow](docs/ZLIB-PACKAGE.md). See the [fixture contract](docs/BUILD-FIXTURE.md) for cleanup, output paths, and safety limits.

## History

[The dated archive](docs/archive/2026-09-05-planning-reset/README.md) preserves the previous planning program, research, backlog, and historical checks. Those workflow commands and completion labels do not govern current work. The [original research guidance](docs/PM-PRD-Initial-Research-Guidance.md) remains seed context; current direction lives in PROJECT.

Shared UI/UX: the consumer [Experience adoption](docs/EXPERIENCE.md) records
applicability; its referenced specifications remain private.

Shared engineering contracts: [Foundations, authority, interfaces and evidence](docs/STANDARDS.md).
The [consumer standards adoption](docs/STANDARDS.md) routes domain contracts;
package/service integration remains a shared candidate proposal.

Current multi-module boot transport: [five-artifact v2 handoff](docs/BOOT-HANDOFF-V2.md). The legacy pair adapter remains unchanged.

Development validation runs `sh tests/check-standards.sh` before the package
fixtures. Its three standards checks require private inputs and remain blocked
in a public-only checkout. Package runtime tooling remains shell/make. Future
shared standards stay with Aether-standards; see [adoption scope](docs/STANDARDS.md).

[Supervised boot handoff](docs/SUPERVISED-HANDOFF.md) provides an optional six-artifact host transport with explicit pins; installation does not activate services.

## License

Original work is licensed under [BSD-2-Clause](LICENSE). Third-party material
retains its own terms. See the [consumer licensing summary](../docs/LICENSING.md) for scope,
contributions and redistribution. Contributors retain copyright in their work.

[Bytecount host package](docs/BYTECOUNT-PACKAGE.md) now exercises pinned userland source through build, registration and binary import; native command execution remains separate.

Contributor workflow and check selection: [Contributing](CONTRIBUTING.md).

Release preparation: [experimental host release scope and gates](docs/HOST-RELEASE.md).

CLI manual: [pkg-mgr(1)](man/pkg-mgr.1). Read it offline with
`mandoc -Tascii man/pkg-mgr.1` from this checkout. For release documentation checks,
run `python3 tests/check-manuals.py --render-required --binary-example`. This requires mandoc, man, a host C compiler and
executes curated examples in a retained private root beneath the checkout.

Package-state format: [pkg-state(5)](man/pkg-state.5). Binary transport: [pkg-binary(5)](man/pkg-binary.5). The manual check renders all three
pages and verifies host lookup from a private staged share/man layout.

## Git workflow

Follow root [source-control and integration policy](../PROJECT.md#source-control-and-integration-authority)
and review `git diff`, `git diff --cached` and the actual proposed tree/message
from the system root. Imported hooks remain private; run required affected checks
and public CI. Required checks and separate review precede integration; use only
the owner-approved public destination.

Security reports: [reporting policy and contact](SECURITY.md).
