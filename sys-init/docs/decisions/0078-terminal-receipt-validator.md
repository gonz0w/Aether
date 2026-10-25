# 0078 — Preserve raw terminal sample receipts before qualification

Implemented standalone host validator, 2026-09-06, BG-058 NT-04 local validator slice.

Implement a standalone allocation-free Rust validator for exactly three ordered
register triples: observation O1, worker status S, observation O2. Store signed
RAX and unmodified RDX/R8 before interpretation. Native rejection carries the
fixed read operation and unsigned errno magnitude; local malformed data carries
an enum cause, never an invented errno. Negative RAX takes precedence over
interpretation of auxiliary registers. Validate boolean encodings on receipt;
reject zero terminal revision before S. After O2, require revision/result/readiness
agreement and the already accepted narrow kind/result mapping.

A live O1 seals the sample without a fact. Any failure seals it, retains the exact
received prefix, and rejects later pushes without overwriting data. A complete
terminal sample retains a fact and all three receipts. Synthetic interruption
may close an incomplete nonempty sample; it invents no missing return. There is
no reset, allocation, retry, syscall, resource release or authority API here.
The caller must still retain owner/token/actual Worker and serialize native reads.

Host-compiled Rust tests will inject malformed booleans, invalid pairs, revision,
result and readiness contradictions, native errors at each position, integer
boundaries, live replies, interruption and sealed-state duplicate attempts.
Two omission controls must fail their named assertions: forgetting O1 on receipt
of S, and representing a local invalid boolean as native errno 71. This is
synthetic logic coverage, not actual producer return or native driver integration.

Add a required offline host Rust gate to check-all, using installed Rust 1.98.0
and edition 2024. This non-POSIX development tool is justified by testing the same
Rust logic intended for the native consumer; it selects no production language
or POSIX runtime dependency. Missing compiler, timeout, empty/missing cases or
failed controls reject. Retain sources, compiler identity, commands and raw logs.
The existing 120-case native consumer stays byte-identical and is not rerun for
an unlinked module. Adapter raw capture and bound driver integration remain the
next native slice, with fresh target evidence and 4 KiB size checks required.

Foundations O/I/E and the scoped quality review apply; no shared pin, ABI, existing
native error contract, unsafe primitive, dependency download or renderer changes.
The new check label uses existing plain stderr progress and JSON summary rules.
Full development checks and inventory/documentation updates are required. No
independent reviewer sign-off or complete NT-04–07/ND-02 conformance is claimed.

## Result, review and remaining work

Nine development gates pass in `out/checks/run-02k_q5um`. The new gate passes
nine named parameterized Rust tests and detects two separately compiled omission
controls at their exact assertions. All four tested source files and the compiler
hash remain unchanged. The eight native consumer inputs and worker/builder inputs
still match decision 0077; its 120-case target witness is not reinterpreted as a
new native run. Evidence: `docs/evidence/terminal-receipt-validator-2026-09-06/`.

Raw receipts are private fixed storage exposed by immutable reference. Receipt
count only increases to three, and sealing prevents replacement after live,
terminal or failed outcomes. Signed native failures preserve even i64::MIN's
unsigned magnitude; invalid auxiliary registers cannot relabel a native error.
Local boolean/revision/coherence/pair causes have no errno field. The tests cover
zero terminal revision, wide values without truncation, equal numeric results
with distinct kinds, and contradictory live status after terminal O1. Synthetic
interruption retains one or two actual supplied returns and no missing values.
The module contains no unsafe code, allocation, OS call or resource destructor.

The caller still must preserve actual Worker/owner/token identity and resources.
Host inputs are explicitly synthetic and prove no producer return, interrupted
syscall or resource ownership. Native Adapter still discards raw values on its
legacy validation path; integrating raw capture and this accumulator behind the
Driver reservation is next and requires fresh target evidence. The native 4 KiB
size limit remains. No current native file or immutable evidence was rewritten.

The first focused run passed before wrapper result/schema and four-source capture
were added; its raw artifacts are retained as preliminary, not final acceptance.
The final full run uses copied Rust module/tests, Python wrapper and check-all
source. Compiler identity and host are recorded; system libraries are not a
hermetic toolchain bundle. Missing tools, timeout or wrong test/control outcomes
cannot pass the required gate. There were no failed builds or test attempts.

Documentation impact: developer prerequisites/check order, quality inventory,
standards/experience adoption, terminal contract and native/planning scope. Existing
machine JSON fields and exit behavior are preserved; progress gains one named
gate. No independent review, shared ABI or production portability is claimed.
