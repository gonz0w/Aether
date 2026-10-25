# Documentation coverage and publication work

This BG-056 record inventories 18 explicit developer entry points: eleven scripts,
three top-level offline standard checkers and four native test runners. The accompanying [JSON inventory](documentation-inventory.json)
records each source hash, literal argparse declarations and existing narrative
reference. It reads source syntax without importing or running builders. Hidden
worker arguments stay visible in the inventory but are not operator APIs.

The scope is developer tooling and experiments. There is no installed production
init command or selected production service-file language. A manual cannot create
those interfaces. Unit-test modules, internal helpers, vendored releases, archives
and retained evidence are excluded from individual command manuals.

## Entry-point coverage

| Entry points | Existing narrative | Missing publication work |
| --- | --- | --- |
| check-all | DEVELOPMENT-CHECKS.md; new source manual below | Independent technical/reader review and target installation/lookup |
| check-static, check-quality-process, check-native-evidence | STATIC-CHECKS.md, QUALITY-PROCESS.md, NATIVE-COVERAGE.md | Source manuals added in decision 0100; independent review and target lookup pending |
| check-runtime-model, check-host-runtime, measure-host-runtime | RUNTIME-MODEL.md, HOST-RUNTIME.md, HOST-MEASUREMENTS.md | Source manuals added in decision 0101; independent review and target lookup pending |
| build-lifecycle, lifecycle-native | LIFECYCLE-V1.md | Separate builder/runner manuals; exact tool/input prerequisites |
| build-native-supervisor, native-supervision | NATIVE-SUPERVISION.md | Variant compatibility matrix and source-matched manuals |
| build-native-io-worker, native-io-stop | NATIVE-IO.md | Profile/input compatibility and failure examples |
| build-native-service-worker, native-init | NATIVE-SERVICE.md, NATIVE-ADAPTER.md | Exact current profile/variant inventory; separate builder/runner manuals |
| check-standards, check-experience, check-distribution | STANDARDS.md, EXPERIENCE.md, DISTRIBUTION.md | Source manuals added in decision 0102; wrapper verification gaps tracked separately |

These are narrative coverage references, not claims that every current option is
already explained. Argument declarations preserve defaults/choices as source text;
they do not evaluate expressions or discover dynamically constructed APIs.

## Configuration and internal interfaces

| Surface | Authority and coverage | Missing work |
| --- | --- | --- |
| Host test descriptors | prototypes/host_runtime/descriptors.py; HOST-RUNTIME.md; descriptor tests | Field/stage/ownership reference and contract evidence added in decision 0106; installed/manual review pending |
| Runtime policy and control | specs/RUNTIME-V0.md, CONTROL-V0.md, CONTROL-BOUNDARY-V0.md, CONTROL-AUTHORITY-V0.md | Per-module public/internal API inventory; native authority/delivery remains separately gated |
| Native resource binding and retained history | specs/NATIVE-DRIVER-BINDING-V0.md, NATIVE-RECEIPT-OWNERSHIP-V0.md, NATIVE-PENDING-HISTORY-V0.md | Profile-specific ownership/error/lifetime manuals with exact witness links |
| Native terminal facts | specs/NATIVE-TERMINAL-EVIDENCE-V0.md; NATIVE-BOUNDARY-REVIEW.md | Complete per-profile ABI review; current boundary inventory is a scoped review |
| Offline standards locks and static-tool JSON | STANDARDS.md, EXPERIENCE.md, DISTRIBUTION.md, STATIC-CHECKS.md | Static-tool/boundary fields and invalid-record controls documented in decision 0112; offline-lock fields and cross-wrapper controls documented in decision 0119; bounded reads/traversal and tool-host closure remain |
| Quality/native evidence catalogs | QUALITY-PROCESS.md, NATIVE-COVERAGE.md and their checkers | Quality inventory field/lifetime reference added in decision 0115; native catalog reference and membership controls added in decision 0125; strict record/read validation remains open |
| Production boot/config/TTY/package interfaces | DISTRIBUTION.md and open backlog | Owner contracts and implementation first; outside this review |

## First source manual and review process

[sys-init-checks(1)](man/sys-init-checks.1) is the canonical mdoc source for the
aggregate developer command. The title is a documentation label, not an installed
executable. It documents actual options, internal modes, streams, exits, output
locations, prerequisites and non-native scope. Narrative guides link to it;
rendered files are evidence, not alternate authoring sources.

When touching an inventoried command, update its source hash/declarations,
reference and documentation disposition in the JSON record. Review its options,
exit paths, environment, side effects, failure artifacts and examples against
source before claiming the manual complete. Do not run arbitrary documentation
code blocks. Manually selected examples must use the checkout or an owned private
output directory. The quality inventory records the relevant guide/manual links.
This inventory is a reviewed snapshot; source-drift enforcement is not yet an
aggregate gate for documentation.

Decision 0099 retains lint, terminal rendering at 78 and 60 columns, HTML output,
selected CLI probes and aggregate checks. The local author inspected the terminal
text; independent technical/reader review and HTML visual inspection are pending.
The macOS mandoc build reports a style notice for explicit `.Os sys-init experimental`;
keep accurate experimental identity instead of its compiled-in NetBSD default.
This is a scoped local documentation choice, owned by the sys-init maintainer and
to be revisited at publication/tool change, not approval of a candidate exception.
Lint exits 1 for that sole STYLE notice; this is not a zero-exit strict-lint
claim. No WARNING or higher diagnostics remain. Initial unavailable host-manual references
and reference-order warnings are retained and corrected using actual tool names
and offline repository references.

Before publishing manuals, a named independent reviewer must verify command
semantics and perform a reader walkthrough. The assembly owner must verify actual
installation paths, section lookup, cross-references and offline target use.
Neither this host rendering nor candidate document checks can satisfy that target
requirement. No shared pin, runtime behavior or sibling repository is changed.

## Checker manuals — decision 0100

Canonical source manuals now also cover
[static checks](man/sys-init-check-static.1),
[quality records](man/sys-init-check-quality.1) and
[native evidence](man/sys-init-check-native-evidence.1). Four of the eighteen
inventoried entry points have manuals. These preserve the different failure
streams and exit codes instead of implying one common protocol. The static
checker has bounded tool subprocesses; the two standalone record audits do not
have their own watchdog. The aggregate supplies its existing gate watchdog.

The same explicit experimental OS style disposition applies to these manuals.
Local CLI probes and 78/60-column rendering are evidence of this scoped source
review; independent review and installed-target lookup remain pending. See
[evidence](evidence/checker-manuals-2026-09-06/README.md).

## Model, host and measurement manuals — decision 0101

Source manuals now cover the [model checker](man/sys-init-check-model.1),
[host checker](man/sys-init-check-host.1) and
[measurement runner](man/sys-init-measure-host.1): seven of eighteen commands.
These document legacy differences: the host checker ignores ordinary arguments
and has no help/version mode; the model rejects unknown arguments with exit 2
and writes a PASS line plus a separate JSON file; measurement uses the existing
JSON/report and exit-64 usage contract. Runtime interfaces remain unchanged.

Selected commands, including a complete measurement run and its deliberate
timeout, are retained with source identities. Instrumented host measurements
remain exploratory and do not qualify native performance. Independent review,
HTML visual inspection and target manual lookup remain pending.

## Standards wrapper manuals — decision 0102

[Foundations](man/sys-init-check-standards.1),
[Experience](man/sys-init-check-experience.1) and
[Distribution](man/sys-init-check-distribution.1) now have source manuals.
Ten of eighteen inventoried commands have manuals. All three wrappers ignore
arguments and run reference checks; their errors and verification order differ.
Three copied-wrapper missing-lock controls verify failure streams without
altering any original lock or release.

Source review identifies remaining Experience lock/symlink/pre-execution
inventory validation and inherited Python optimization handling for
Experience/Distribution. BG-056 tracks those implementation gaps; this manual
work neither fixes them nor authorizes changing immutable releases. All reference
probes used an assert-enabled Python environment. Independent reader/HTML visual
review and target lookup remain pending.

## Wrapper findings resolved — decision 0103

Experience now rejects malformed pins, symlinks and incomplete/unsafe inventories
before executing its checker. Experience/Distribution explicitly run the child
with assertions enabled. Their manuals and source identities are updated;
successful text and release pins stay unchanged. The decision-0102 findings above
are historical; their scoped implementation fixes have synthetic controls and
real-release compatibility evidence. Independent review and other gaps remain.

## Builder manuals — decision 0104

All four builders now have canonical source manuals: lifecycle, legacy native
supervisor, I/O worker and service worker. Fourteen of eighteen commands have
manuals. The corresponding native-runner manuals in the table above remain open.
All choices/operands are covered, including the twenty supervisor variants and
mutually exclusive I/O profiles. Actual output reuse rules and differing receipt
schemas are documented; build acceptance remains separate from native execution.

Twelve CLI probes and four fresh default-profile builds pass. Lifecycle and
supervisor raw/envelope bytes and I/O ELF/envelope bytes match retained decision
0098/0097 artifacts; the service ELF passes its existing structural checks. This
does not requalify every variant/input combination. Source and receipt identity
review permits retaining earlier variant tests without another target run for
these documentation-only edits. Independent/HTML visual review and target lookup
remain pending.

## Native runner manuals and copied dependency — decision 0105

All eighteen inventoried developer entry points now have canonical source
manuals. The final four cover lifecycle, native supervision, I/O stop and native
init execution. They describe actual kernel/QEMU effects and separate legacy
list reports/timeouts from modern schema-tagged records and owned-group cleanup.
Detailed configuration/API documentation and independent/HTML/target review
remain open; manual existence does not establish publication conformance.

Review found that the I/O runner's copied builder omitted bounded_tools.py,
introduced in decision 0098. The capture now includes and fingerprints the helper.
A real isolated-copy regression and helper-removal control exercise imports;
a fresh copied io-stop build preserves the retained raw/envelope bytes. This
fix changes host input capture only, not target code or semantic test oracles.
No new native execution is claimed for the documentation/capture slice.

## Host descriptor reference — decision 0106

[HOST-DESCRIPTORS.md](HOST-DESCRIPTORS.md) is the local canonical narrative/API
reference for the implemented host descriptor subset. It covers all thirteen
fields, graph/model restrictions, preparation and activation, file/content
ownership, defaults and environment precedence, error stages and unsupported
reload/concurrency policies. Six required host contract tests include the
[temporary executable example](examples/host-descriptor.py). This example is
documentation support outside the eighteen inventoried developer entry points;
it has no supported command-line interface. The host gate executes it explicitly.

The reference is not an installed configuration/API manual or full production
format adoption. Remaining record/API families, independent review and target
lookup remain open. No runtime behavior or shared pin changes in this slice.

## Static record fields — decision 0112

[STATIC-RECORDS.md](STATIC-RECORDS.md) covers the twelve static-tool settings,
boundary record/site fields, selected-source lifetime and success/failure JSON.
Five focused tests supplement existing static controls. Strict record parsing,
consistent structured failures, ordinary-file/parent-symlink policy, metadata
identity across a standalone check and complete tool closure remain BG-056 gaps.
Other record/API families and independent publication review remain open.

## Offline lock reference — decision 0119

[OFFLINE-LOCKS.md](OFFLINE-LOCKS.md) covers all five lock fields and the three
family/path mappings, actual text parsing, manifest checks and child environment.
Synthetic cross-wrapper tests cover accepted layouts and rejection before child
invocation. Ordinary-file/read bounds, verification-to-execution identity and
interpreter closure remain BG-056 work. No wrapper or release bytes changed.

## Native catalog reference — decision 0125

[NATIVE-EVIDENCE-RECORDS.md](NATIVE-EVIDENCE-RECORDS.md) records catalog/case fields,
I/O and init report selection, receipt/artifact correspondence, envelope/serial
rules, success JSON and actual parsing/lifetime gaps. Required-file membership
and top-level rejection controls supplement retained semantic tests. Checker and
catalog bytes are unchanged; strict parsing and bounded reads remain BG-056 work.

Decision 0147 adds the nineteenth entry point, check-extended-host.py, with its
EHT-01 reference and manual. It is an optional local campaign, outside the normal
gates; no installed operator command or scheduler is claimed.
