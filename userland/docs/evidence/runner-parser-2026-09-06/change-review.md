# UL-059 pure carrier decoder and selector

Before code: C17, fixed private arrays, no allocation/transport/authority. Decode
exact 224-byte AERUN001 records to owned six-string storage only after complete
validation. Reject malformed fields, lengths/counts, terminators/padding and wrong
argv0. Selection revalidates its typed input, recognizes sole help/version,
optional leading --, name-only command, max four copied child strings, exact
LC_ALL=C environment. Invalid input and non-launch actions leave output untouched;
callers must dispatch on returned action, never reuse output after a failure.
No pointer retention, truncation, shell interpretation or ambient environment.

Tests: table-driven exact action/argument cases, byte/count boundaries, all
reserved/unused bytes and active slot corruption, mutation-after-copy, null and
malformed typed input. Test-only skip-reserved and reinterpret-child-help mutants
must fail named oracles. UBSan explicitly selected (ASan prerequisite still open).
Use existing pinned Clang/SDK, C17 owner diagnostics plus strict prototype,
conversion/sign/shadow/pedantic checks; no suppressions planned. Build native
x86_64-musl object and inspect imports (not native execution). Existing 21 command
host tests and quality/format/grammar required; no native adapter/driver changes.
Thirty-second owned host commands, clean environment, private build roots,
compiler/runtime/source/plan hashes and every attempt retained. Independent review
pending; no public help output, status mapping, native carrier or CLI acceptance.
