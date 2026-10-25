# Static checks for contributors

Experimental developer tooling, decision 0095 / BG-056. Run from the repository
root with Python 3.10+ and installed Rust 1.98.0 including rustfmt and Clippy:

```sh
python3 scripts/check-static.py
python3 scripts/check-all.py
```

A successful static run reports JSON `schema: sys-init-static-v1`, `result: pass`,
file counts, source hashes, Python identity and rustfmt identity. The aggregate
runner requires this gate before native-evidence and runtime checks. Static
success does not establish behavior, native execution or release acceptance.

| Scope | Required check | Deliberate limits |
| --- | --- | --- |
| Python under scripts, tests, prototypes and .githooks; top-level docs checkers | Compile source without executing it or writing bytecode | Syntax and compiler context only; no style, type, dependency or all-version claim |
| tests/native_sample_receipts.rs and tests/native_pending_history.rs | Exact output from pinned rustfmt, edition and style edition 2024, skip_children=true | Host test files only; native child modules are never formatted |
| Native Rust/C, upstream, generated, vendor and retained evidence | Existing selected build/runtime checks continue | Outside this formatter scope; not declared lint-conformant |

`docs/static-tools.json` pins the developer formatter version, executable digest,
arguments and source scope. It is not an Aether release pin. Decision 0151 adds Linux aarch64 identities for the same Rust version, alongside
macOS arm64. Other hosts report blocked;
add a reviewed tool identity with actual tests before advertising their support.
The formatter comes from the existing Rust toolchain, is a host-only development
dependency and does not ship in the target. It adds no Cargo package or runtime
library. Its upstream terms remain separate from original BSD-2-Clause code.
No checker downloads or installs tools. The release pins remain v0.1.0.

Each source is at most 1 MiB, with at most 1,000 files and 16 MiB total. Each
trusted tool invocation has a ten-second deadline and a 4 MiB merged output cap;
a private input file preserves literal bytes. The checker owns the non-detaching
tool process group and terminates it on failure. The aggregate adds its existing
60-second stage watchdog. Temporary input files are removed on exit. Tool and
source hashes are checked before/after. These checks are not confinement against
a malicious local actor changing tool files concurrently.

Help/version exit 0 on stdout. Invalid arguments exit 64 with stderr diagnostics.
Operational failures (including syntax/format differences or output overflow)
exit 1; unavailable/unreviewed/mismatched tools and timeouts exit 2. Failure JSON
is on stdout and escaped diagnostic text is on stderr. There is no color,
animation, operator state or service mutation. Redirect both streams to preserve
a standalone attempt; check-all retains them automatically.

For a formatting difference, inspect the named host test file and compare the
formatter output before applying it. Use the pinned command from
`docs/static-tools.json` with the file supplied on stdin; do not recursively
format native modules. For tool mismatch, restore the reviewed installed version
or make a separately reviewed lock update with evidence. Never replace a digest
only to suppress a failure. Unsupported host/required-tool failures are gaps,
not approved exceptions.

The nine harness cases in `tests/test_harness_static.py` exercise invalid syntax
without executing input, format drift, empty scope, oversized input, tool digest
and version mismatches, missing tools, timeout, nonzero exit, output overflow,
literal input and help/version/usage streams. Existing Rust behavior and omission
tests still run in the separate sample-receipts gate.

Native/C formatter migration, full unsafe/FFI and suppression
inventories, Python semantic/static analysis and supported-host expansion remain
BG-056. Extended workloads and scheduling remain BG-054. This scoped first gate
does not claim complete candidate Coding adoption or provision Mermaid rendering.

## Clippy and boundary coverage — decision 0096

The required gate now also runs pinned `clippy-driver` 1.98.0 with Rust edition
2024, `--test --emit=metadata -D clippy::all` on the two host harnesses and their
pure receipt/history modules. It copies those four files into a private tree;
no native trap module is compiled or executed by this host lint path. Metadata
outputs and the private tree are removed. The existing ten-second/4 MiB tool
bounds and before/after executable/source identity checks apply. Default Rust
compiler warnings remain visible in `clippy_diagnostics`; the expected unused
shared-method warning in the smaller history harness is not suppressed. Default
Clippy group findings fail; restriction/pedantic groups are not enabled wholesale.

`docs/native-boundaries.json` inventories 50 textual unsafe/entry/assembly sites
in 13 first-party files. Missing/new files, changed site lists and source-hash
drift fail with a review-required diagnostic. This is change detection around
[the source review](NATIVE-BOUNDARY-REVIEW.md), not a semantic parser or evidence
that every unsafe operation is sound. Review source, producer and compiler impacts
before updating an inventory digest. Legacy profiles remain inventoried with
explicit unresolved review scope. Eleven static-harness tests now include a real
Clippy rejection and boundary-inventory drift/omission controls.

The executable hashes do not pin every system/toolchain dynamic library; full
host tool dependency closure remains part of CD-01/04 migration. No release pin,
C compiler flag, native ABI or target-source formatting changes in this step.

The canonical [static-check manual](man/sys-init-check-static.1) records options,
streams, status distinctions, tool prerequisites and temporary artifact lifetime.

Decision 0112 adds the [field-level record reference](STATIC-RECORDS.md) for
static tools, boundary inventory and results. It separates enforced checks
from descriptive metadata and records strict parsing/identity/ordinary-file
gaps under BG-056. Five additional record-contract tests cover source scope,
byte accounting, path rejection and textual/duplicate boundary behavior.
The implementation and current settings/inventory bytes are unchanged.

Decision 0113 strictly validates static settings and boundary records before
tool lookup: exact schema/fields/types, bounded JSON/depth/collections/strings,
duplicate-key and path/digest checks. Malformed records use structured failure
without command execution. Maintained record bytes and published pins remain
unchanged; ordinary-file/atomic identity and tool closure remain BG-056 work.
See docs/STATIC-RECORDS.md for precise limits and decision 0113 for evidence.

Decision 0114 validates ordinary selected input files and symlink components
within the supplied root, bounds reads and checks file identity around them.
Standalone static checks parse captured JSON and reject changed record bytes
before success. FIFO and controlled replacement/growth/metadata cases supplement
existing tests. Hostile directory races and transitive tool closure remain
outside this result; see docs/STATIC-RECORDS.md for precise scope.
