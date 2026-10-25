# Static-check configuration and boundary records

Local reference for [check-static.py](../scripts/check-static.py),
[static-tools.json](static-tools.json) and
[native-boundaries.json](native-boundaries.json). These are trusted maintainer
inputs to experimental host tooling, not released Aether standards, service
configuration, native ABIs or authenticated tool manifests. See the
[command manual](man/sys-init-check-static.1) for invocation and exit behavior.
This describes the implemented reader including decision 0113 validation; it
does not establish an authenticated public interchange format.

## Static-tool fields

The current settings object contains these twelve fields. The reader requires the exact field set and schema; omission and unknown keys
reject before tool lookup.

| Field | Maintained representation | Consumer behavior |
| --- | --- | --- |
| `schema` | `sys-init-static-tools-v1` | Exact required schema label |
| `rust_toolchain` | String, currently `1.98.0` | Passed literally after `rustup which --toolchain` for each tool |
| `rustfmt_version` | Exact version string | Compared with stripped decoded `rustfmt --version` output |
| `rustfmt_sha256` | Object mapping host keys to lowercase SHA-256 strings | Selects `platform.system() + "-" + platform.machine()`; absent host blocks before rustfmt lookup |
| `rustfmt_args` | Ordered string array | Supplied to rustfmt with source bytes on stdin; current edition/style edition 2024 and `skip_children=true`; output must equal original bytes |
| `rust_sources` | Nonempty array of checkout-relative source paths | Explicit input selection, formatting and one Clippy invocation per listed harness; currently two host Rust test files |
| `python_roots` | Array of directory paths | Recursive `*.py` discovery; currently scripts, tests, prototypes and .githooks |
| `python_top_level` | Array of directory paths | Immediate `*.py` children only; currently docs, excluding its nested vendor/evidence trees |
| `clippy_version` | Exact version string | Compared with stripped decoded `clippy-driver --version` output |
| `clippy_sha256` | Host-to-SHA-256 object | Host lookup occurs after rustfmt identification; missing host blocks Clippy execution |
| `clippy_args` | Ordered string array | Current Rust2024 test/metadata mode and `-D clippy::all`; supplied before copied source and generated `-o` path |
| `clippy_modules` | Array of checkout-relative paths | Adds imported modules to selected bytes and the private Clippy tree; the field is required and may be empty |

The current reviewed host key is `Darwin-arm64`. No automatic host alias or
fallback is provided. Tool paths come from rustup stdout, not this object.
SHA-256 is checked before executing the identified tool's version command;
a matching digest does not authenticate the provider or pin dynamic libraries.
`rustup` itself is resolved through PATH and is not hash-pinned by these fields.
The same tool files are hashed again after checks. Arguments are argv elements,
not shell text. Changing arguments, host pins or scope requires review and new
evidence, not merely replacing a hash until a check passes.

## Selection, execution and lifetime

1. Strictly parse and check the native boundary inventory, then strictly parse
   settings. Only afterward resolve and identify rustfmt, then Clippy.
2. Collect source paths into a set. Overlapping selections collapse for collection;
   duplicate entries within a settings path list reject during validation.
   Missing discovery directories can contribute zero files silently. Reject a
   wholly empty scope, empty Rust source list or absence of Python files.
3. Enforce at most 1,000 selected paths, 1 MiB per source and 16 MiB combined
   actual bytes. Reject a symlink component or path outside the supplied root.
   Read and retain bytes before checking them. Decision 0114 requires ordinary
   files and checks identity and metadata around
   bounded nonblocking reads; concurrent hostile directory replacement is not
   an atomic-snapshot guarantee.
4. Compile Python syntax without executing code or writing bytecode. Compare
   rustfmt output byte-for-byte. Copy the listed Rust harnesses and modules into
   a temporary tree, then run Clippy there; temporary metadata/tree are removed.
5. Compare source bytes and tool hashes again, then repeat boundary checking.
   Return the report only on success. Settings and boundary JSON are captured
   before parsing/tools, then safely
   reread and compared byte-for-byte before success, including unused metadata.
   The aggregate also checks source identities; neither check makes reads atomic.

Each trusted tool call has a ten-second deadline and 4 MiB merged-output cap.
No downloads or installations occur. Tool-owned groups must not detach; command
capture and cleanup are scoped host behavior, not confinement. Selected-byte
limits exclude tool executable size, settings/inventory JSON size, private
compiler memory and all transitive tool dependencies.

## Native-boundary fields

The current object has `schema` (`sys-init-native-boundaries-v1`), descriptive
`scope`, and `records`. All fields participate in syntax validation; only `records` drives source
comparison. Schema is exact and scope is a nonempty bounded string.
Each current record contains:

| Field | Maintained representation | Enforced by the reader |
| --- | --- | --- |
| `file` | Checkout-relative Rust/C path under prototypes | Unique key; exact membership in the discovered boundary-file set |
| `sha256` | Lowercase SHA-256 of the entire file | Exact equality with the current file digest |
| `sites` | Ordered array of `{line, text}` objects | Exact list equality with reconstructed sites |
| `review` | Review disposition text | String syntax checked, not authenticated |
| `reference` | Local review-document path | Normalized relative syntax checked, not resolved here |
| `owner` | Responsible maintainer text | String syntax checked; not reviewer approval |
| `follow_up` | Stable backlog references and limitations | String syntax checked; not executed or authenticated |

Discovery recursively examines `.rs` and `.c` files under prototypes. Each
matching line contains the word `unsafe`, exact `extern "C"`, or `__asm__`.
The stored line number is one-based; text is the entire line with leading and
trailing whitespace stripped. One matching line produces one site, regardless
of occurrence count. Comments and string literals can match. This is textual
drift detection, not an AST parser or a complete unsafe/FFI inventory. Files
without matching lines do not need records. Empty discovery, duplicate file
records, changed file membership, hash drift or changed ordered sites fail.
Changing unrelated source lines still changes the whole-file hash.

Unknown fields reject at every fixed record level, including sites. Site line
numbers must be positive integers, with booleans explicitly rejected.
Metadata cannot
supply a missing native witness or convert an inventory-only review into
soundness approval. Preserve historic evidence and revise current records only
after the owning source review.

## Result and failure records

Successful stdout JSON uses `schema: sys-init-static-v1`, `result: pass`, `host`,
`python`, `rustfmt`, `tool_sha256`, `clippy`, `clippy_sha256`, `boundary_files`,
`python_files`, `rust_files`, `clippy_diagnostics`, `sources` and descriptive
`scope`. `sources` maps selected relative paths to their input-byte digests;
`clippy_diagnostics` maps harness paths to decoded merged compiler output.
Counts describe this selected scope, not runtime coverage. A pass has no native
execution claim. There is no timestamp, signer or release authorization field.

Caught OSError/ValueError/SyntaxError failures use the same schema with
`result: fail` or `blocked` and `diagnostic`; an escaped diagnostic is also
printed on stderr. A `Blocked` error exits 2; ordinary caught failure exits 1.
Malformed settings or boundary schemas/types now raise ValueError and follow
this structured failure path, before tool lookup. Preserve both
streams and the exit status; an absent report is not a pass.

Examples of enforced rejection: an unreviewed formatter digest blocks before
its version executable runs; a selected symlink rejects; a duplicate boundary
file record rejects; adding a source line invalidates the whole-file digest.
Existing and new controls are in [static harness tests](../tests/test_harness_static.py)
and [record contract tests](../tests/test_harness_static_records.py).

## Parser limits and remaining work

Decision 0113 reads at most 1 MiB plus one byte per JSON record, rejects files
over 1 MiB, invalid UTF-8/JSON, duplicate keys at any depth and NaN/Infinity.
An explicit scan bounds nesting to 32 levels, excluding brackets inside strings.
Records require exact field sets and schemas. Lists contain at most 1,000 items;
Rust sources, argument lists, boundary records and site lists must be nonempty.
Host maps contain 1–1,000 entries. Strings contain 1–4,096 Unicode characters,
encode as UTF-8, and contain no ASCII control/DEL characters. Digests require
64 lowercase hexadecimal characters. Relative paths reject absolute paths,
backslashes, empty segments, `.` and `..`. Duplicate settings path entries reject.
Boundary file membership, line ordering and exact text still undergo source
comparison. Host keys are bounded strings, not a new host naming standard.

Metadata validation is syntactic: reference paths are not dereferenced and owner
strings are not signatures. Argument arrays remain trusted maintainer policy;
validation does not authorize arbitrary compiler options. Existing source helper
unit tests may call selection functions directly, bypassing record parsing; the
CLI path validates before invoking tools.

Decision 0114 rejects symlink components beneath the supplied root (and a root
that is itself a symlink), and requires ordinary files for selected sources and
JSON. Ancestors above that root are outside this check. Opens use O_NONBLOCK and
O_NOFOLLOW where available; fstat verifies regular type and device/inode against
pre-open lstat. Reads are capped and device/inode/size/mtime are checked afterward.
Missing discovery directories still contribute no files; configured dangling
symlinks reject. Record bytes are compared across the standalone run. Source
boundary text and hash are derived from the same captured bytes.

BG-056 still owns complete tool dependency closure and remaining record/API
families. These checks do not guarantee an atomic snapshot, reject every hostile
parent-directory replacement race, or bound blocking regular-file filesystem I/O.
Transient changes restored before final comparison may go undetected. Identical
replacement record bytes are acceptable to the final byte-comparison rule.
Independent
technical/reader review and installed field-reference manuals remain open.
